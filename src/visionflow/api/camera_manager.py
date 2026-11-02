from __future__ import annotations

import re
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import cv2


class CameraManager:
    def __init__(self, model_path: Path, max_cameras: int = 4):
        self.model_path = model_path
        self.max_cameras = max_cameras
        self._cameras: dict[str, dict] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _parse_source(source: str) -> tuple[str | int, str]:
        if not isinstance(source, str):
            raise ValueError("Camera source must be text.")
        value = source.strip()
        if re.fullmatch(r"\d{1,3}", value):
            return int(value), f"USB / device {value}"
        if len(value) > 512:
            raise ValueError("Camera source must be 512 characters or fewer.")
        try:
            parsed = urlsplit(value)
            host = parsed.hostname
            port = parsed.port
        except ValueError as error:
            raise ValueError("The RTSP/RTSPS URL is invalid.") from error
        if parsed.scheme not in {"rtsp", "rtsps"} or not host:
            raise ValueError("Use a camera index (for example 0) or an RTSP/RTSPS URL.")
        if ":" in host and not host.startswith("["):
            host = f"[{host}]"
        if port:
            host = f"{host}:{port}"
        safe_url = urlunsplit((parsed.scheme, host, "/stream", "", ""))
        return value, safe_url

    def add_camera(self, name: str, source: str) -> dict:
        if not isinstance(name, str):
            raise ValueError("Camera name must be text.")
        clean_name = " ".join(name.strip().split())[:80]
        if not clean_name:
            raise ValueError("Camera name is required.")
        parsed_source, source_label = self._parse_source(source)
        with self._lock:
            if len(self._cameras) >= self.max_cameras:
                raise RuntimeError(f"You can connect up to {self.max_cameras} cameras.")
            camera_id = uuid.uuid4().hex[:12]
            camera = {
                "id": camera_id,
                "name": clean_name,
                "source": parsed_source,
                "source_label": source_label,
                "status": "connecting",
                "counts": {},
                "detections_total": 0,
                "fps": 0.0,
                "last_seen": None,
                "error": None,
                "frame": None,
                "frame_lock": threading.Lock(),
                "stop_event": threading.Event(),
                "capture": None,
                "thread": None,
            }
            self._cameras[camera_id] = camera
        self._start_worker(camera)
        return self._public_camera(camera)

    def _start_worker(self, camera: dict) -> None:
        camera["stop_event"].clear()
        worker = threading.Thread(
            target=self._run_camera,
            args=(camera,),
            name=f"visionflow-camera-{camera['id']}",
            daemon=True,
        )
        camera["thread"] = worker
        worker.start()

    def start_camera(self, camera_id: str) -> dict:
        with self._lock:
            camera = self._cameras.get(camera_id)
            if camera is None:
                raise KeyError(camera_id)
            worker = camera["thread"]
            if worker and worker.is_alive():
                if camera["status"] != "offline":
                    raise RuntimeError("Camera is already running or connecting.")
                camera["stop_event"].set()
                if camera["capture"] is not None:
                    camera["capture"].release()
        if worker and worker.is_alive():
            worker.join(timeout=2)
            if worker.is_alive():
                raise RuntimeError("Camera is still closing its previous stream. Try again shortly.")
        with self._lock:
            if self._cameras.get(camera_id) is not camera:
                raise KeyError(camera_id)
            camera["status"] = "connecting"
            camera["error"] = None
            camera["counts"] = {}
            self._start_worker(camera)
            return self._public_camera(camera)

    def stop_camera(self, camera_id: str) -> bool:
        with self._lock:
            camera = self._cameras.get(camera_id)
            if camera is None:
                return False
            camera["stop_event"].set()
            capture = camera["capture"]
            if capture is not None:
                capture.release()
            camera["status"] = "stopped"
            return True

    def remove_camera(self, camera_id: str) -> bool:
        with self._lock:
            camera = self._cameras.pop(camera_id, None)
            if camera is None:
                return False
            camera["stop_event"].set()
            if camera["capture"] is not None:
                camera["capture"].release()
            return True

    def get_camera(self, camera_id: str) -> dict | None:
        with self._lock:
            camera = self._cameras.get(camera_id)
            return self._public_camera(camera) if camera else None

    def list_cameras(self) -> list[dict]:
        with self._lock:
            return [self._public_camera(camera) for camera in self._cameras.values()]

    @staticmethod
    def _public_camera(camera: dict) -> dict:
        return {
            "id": camera["id"],
            "name": camera["name"],
            "source": camera["source_label"],
            "status": camera["status"],
            "counts": dict(camera["counts"]),
            "detections_total": camera["detections_total"],
            "fps": round(camera["fps"], 1),
            "last_seen": camera["last_seen"],
            "error": camera["error"],
        }

    def stream(self, camera_id: str):
        while True:
            with self._lock:
                camera = self._cameras.get(camera_id)
                if camera is None:
                    return
                frame_lock = camera["frame_lock"]
                stop_event = camera["stop_event"]
            with frame_lock:
                frame = camera["frame"]
            if frame is not None:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            elif stop_event.is_set():
                return
            time.sleep(0.08)

    def _run_camera(self, camera: dict) -> None:
        try:
            from ultralytics import YOLO

            if not self.model_path.is_file():
                raise FileNotFoundError("The trained model weights are not available.")
            model = YOLO(str(self.model_path))
            while not camera["stop_event"].is_set():
                capture = cv2.VideoCapture(camera["source"])
                with self._lock:
                    camera["capture"] = capture
                capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                if not capture.isOpened():
                    capture.release()
                    camera["status"] = "offline"
                    camera["error"] = "Unable to connect. Check the source and network."
                    camera["stop_event"].wait(5)
                    continue

                camera["status"] = "online"
                camera["error"] = None
                previous_frame_time = time.perf_counter()
                while not camera["stop_event"].is_set():
                    success, frame = capture.read()
                    if not success:
                        camera["status"] = "offline"
                        camera["error"] = "Video stream interrupted. Reconnecting..."
                        break
                    result = model.track(frame, persist=True, verbose=False)[0]
                    annotated_frame = result.plot()
                    encoded, jpeg = cv2.imencode(".jpg", annotated_frame)
                    if encoded:
                        with camera["frame_lock"]:
                            camera["frame"] = jpeg.tobytes()
                    counts: dict[str, int] = {}
                    for class_id in result.boxes.cls.int().cpu().tolist() if result.boxes is not None else []:
                        class_name = str(result.names[class_id])
                        counts[class_name] = counts.get(class_name, 0) + 1
                    now = time.perf_counter()
                    elapsed = now - previous_frame_time
                    previous_frame_time = now
                    camera["fps"] = 1 / elapsed if elapsed else 0
                    camera["counts"] = counts
                    camera["detections_total"] += sum(counts.values())
                    camera["last_seen"] = datetime.now(timezone.utc).isoformat()
                capture.release()
                with self._lock:
                    camera["capture"] = None
                if not camera["stop_event"].is_set():
                    camera["stop_event"].wait(2)
        except (FileNotFoundError, ImportError, RuntimeError, OSError, cv2.error):
            camera["status"] = "offline"
            camera["error"] = "The model could not start this camera. Check the trained weights and server logs."
        finally:
            capture = camera.get("capture")
            if capture is not None:
                capture.release()
            if camera["stop_event"].is_set():
                camera["status"] = "stopped"
