from __future__ import annotations

import threading
import uuid
from pathlib import Path

import cv2
import yaml
from flask import Flask, abort, jsonify, render_template, request, send_from_directory, url_for
from werkzeug.utils import secure_filename

from visionflow.api.camera_manager import CameraManager


def discover_project_root() -> Path:
    candidates = [Path.cwd(), *Path(__file__).resolve().parents]
    for candidate in candidates:
        if (candidate / "configs" / "pipeline_config.yaml").is_file() or (candidate / "weights" / "best.pt").is_file():
            return candidate
    return Path.cwd()


PROJECT_ROOT = discover_project_root()
CONFIG_PATH = PROJECT_ROOT / "configs" / "pipeline_config.yaml"
MAX_UPLOAD_SIZE = 100 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".mp4", ".mov", ".avi", ".mkv"}


def resolve_model_path() -> Path:
    if CONFIG_PATH.exists():
        with CONFIG_PATH.open(encoding="utf-8") as config_file:
            config = yaml.safe_load(config_file) or {}
        configured_path = Path(config.get("model", {}).get("trained_weights", "weights/best.pt"))
        return configured_path if configured_path.is_absolute() else PROJECT_ROOT / configured_path
    return PROJECT_ROOT / "weights" / "best.pt"


MODEL_PATH = resolve_model_path()
UPLOAD_DIR = PROJECT_ROOT / "data" / "outputs" / "uploads"
PROCESSED_DIR = PROJECT_ROOT / "data" / "outputs" / "predictions"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__, template_folder="template", static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE

camera_manager = CameraManager(MODEL_PATH)
_model = None
_model_lock = threading.Lock()
_inference_lock = threading.Lock()


def get_model():
    global _model
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Trained model not found: {MODEL_PATH}")
    with _model_lock:
        if _model is None:
            from ultralytics import YOLO

            _model = YOLO(str(MODEL_PATH))
    return _model


def model_details(include_classes: bool = False) -> dict:
    exists = MODEL_PATH.is_file()
    details = {
        "available": exists,
        "name": MODEL_PATH.name,
        "path": str(MODEL_PATH.relative_to(PROJECT_ROOT)) if MODEL_PATH.is_relative_to(PROJECT_ROOT) else MODEL_PATH.name,
        "size_mb": round(MODEL_PATH.stat().st_size / (1024 * 1024), 1) if exists else None,
        "classes": [],
    }
    if exists and include_classes:
        try:
            class_names = get_model().names
            details["classes"] = list(class_names.values()) if isinstance(class_names, dict) else list(class_names)
        except (FileNotFoundError, RuntimeError, OSError, ImportError, ValueError, EOFError):
            details["available"] = False
            details["error"] = "The checkpoint exists but could not be loaded."
    return details


def page_context(active_page: str, **context) -> dict:
    return {
        "active_page": active_page,
        "model": model_details(),
        **context,
    }


@app.get("/")
def overview():
    return render_template("index.html", **page_context("overview"))


@app.get("/cameras")
def cameras_page():
    return render_template("cameras.html", **page_context("cameras"))


@app.get("/analytics")
def analytics_page():
    return render_template("analytics.html", **page_context("analytics"))


@app.get("/model")
def model_page():
    return render_template("model.html", **page_context("model"))


@app.get("/inference")
def inference_page():
    return render_template("inference.html", **page_context("inference"))


@app.get("/about")
def about():
    return render_template("about.html", **page_context("about"))


@app.get("/contact")
def contact():
    return render_template("contact.html", **page_context("contact"))


@app.get("/api/overview")
def overview_data():
    camera_data = camera_manager.list_cameras()
    online_cameras = sum(camera["status"] == "online" for camera in camera_data)
    detections = sum(sum(camera["counts"].values()) for camera in camera_data)
    active_model = model_details(include_classes=True)
    return jsonify({
        "camera_count": len(camera_data),
        "online_cameras": online_cameras,
        "detections": detections,
        "model": active_model,
        "cameras": camera_data[:4],
    })


@app.get("/api/cameras")
def list_cameras():
    return jsonify({"cameras": camera_manager.list_cameras(), "limit": camera_manager.max_cameras})


@app.post("/api/cameras")
def add_camera():
    payload = request.get_json(silent=True) or {}
    try:
        camera = camera_manager.add_camera(payload.get("name", ""), payload.get("source", ""))
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 409
    return jsonify({"camera": camera}), 201


@app.post("/api/cameras/<camera_id>/stop")
def stop_camera(camera_id: str):
    if not camera_manager.stop_camera(camera_id):
        return jsonify({"error": "Camera not found"}), 404
    return jsonify({"camera": camera_manager.get_camera(camera_id)})


@app.post("/api/cameras/<camera_id>/start")
def start_camera(camera_id: str):
    try:
        camera = camera_manager.start_camera(camera_id)
    except KeyError:
        return jsonify({"error": "Camera not found"}), 404
    except RuntimeError as error:
        return jsonify({"error": str(error)}), 409
    return jsonify({"camera": camera})


@app.delete("/api/cameras/<camera_id>")
def delete_camera(camera_id: str):
    if not camera_manager.remove_camera(camera_id):
        return jsonify({"error": "Camera not found"}), 404
    return jsonify({"deleted": True})


@app.get("/api/cameras/<camera_id>/stream")
def camera_stream(camera_id: str):
    if camera_manager.get_camera(camera_id) is None:
        abort(404)
    return app.response_class(
        camera_manager.stream(camera_id),
        mimetype="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-store"},
    )


@app.get("/api/model")
def model_data():
    return jsonify(model_details(include_classes=True))


@app.get("/api/analytics")
def analytics_data():
    cameras = camera_manager.list_cameras()
    class_counts: dict[str, int] = {}
    for camera in cameras:
        for class_name, count in camera["counts"].items():
            class_counts[class_name] = class_counts.get(class_name, 0) + count
    return jsonify({
        "camera_count": len(cameras),
        "online_cameras": sum(camera["status"] == "online" for camera in cameras),
        "detections": sum(class_counts.values()),
        "classes": class_counts,
        "cameras": cameras,
    })


@app.post("/api/inference")
def run_inference():
    uploaded_files = [file for file in request.files.getlist("files") if file.filename]
    if not uploaded_files:
        return jsonify({"error": "Choose at least one image or video to process."}), 400

    validated_uploads = []
    for uploaded_file in uploaded_files:
        original_name = secure_filename(uploaded_file.filename or "")
        suffix = Path(original_name).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            return jsonify({"error": f"Unsupported file type: {original_name or 'unknown'}"}), 400
        validated_uploads.append((uploaded_file, original_name, suffix))

    try:
        model = get_model()
    except (FileNotFoundError, RuntimeError, OSError) as error:
        return jsonify({"error": str(error)}), 503

    results = []
    with _inference_lock:
        for uploaded_file, original_name, suffix in validated_uploads:
            request_id = uuid.uuid4().hex
            input_path = UPLOAD_DIR / f"{request_id}{suffix}"
            output_suffix = ".jpg" if suffix in {".jpg", ".jpeg", ".png", ".webp"} else ".mp4"
            output_name = f"{request_id}{output_suffix}"
            output_path = PROCESSED_DIR / output_name
            uploaded_file.save(input_path)

            try:
                if output_suffix == ".jpg":
                    image = cv2.imread(str(input_path))
                    if image is None:
                        return jsonify({"error": f"Could not read image: {original_name}"}), 400
                    prediction = model.predict(image, verbose=False)[0]
                    if not cv2.imwrite(str(output_path), prediction.plot()):
                        raise OSError("Could not save the annotated image.")
                    detections = len(prediction.boxes)
                else:
                    detections, frame_count = process_video(model, input_path, output_path)
                    if frame_count == 0:
                        return jsonify({"error": f"Could not read video: {original_name}"}), 400
            except (RuntimeError, OSError, cv2.error) as error:
                return jsonify({"error": f"Could not process {original_name}: {error}"}), 500
            finally:
                input_path.unlink(missing_ok=True)

            results.append({
                "name": original_name,
                "detections": detections,
                "url": url_for("media", filename=output_name),
                "type": output_suffix[1:],
            })
    return jsonify({"results": results})


def process_video(model, input_path: Path, output_path: Path) -> tuple[int, int]:
    capture = cv2.VideoCapture(str(input_path))
    if not capture.isOpened():
        capture.release()
        return 0, 0

    fps = capture.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(
        str(output_path),
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        (width, height),
    )
    if not writer.isOpened():
        capture.release()
        raise OSError("Could not initialize the output video encoder.")

    detections = 0
    frame_count = 0
    try:
        while True:
            success, frame = capture.read()
            if not success:
                break
            prediction = model.track(frame, persist=True, verbose=False)[0]
            detections += len(prediction.boxes)
            writer.write(prediction.plot())
            frame_count += 1
    finally:
        capture.release()
        writer.release()
    return detections, frame_count


@app.get("/media/<path:filename>")
def media(filename: str):
    return send_from_directory(PROCESSED_DIR, filename)


@app.errorhandler(413)
def request_too_large(_error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "The upload exceeds the 100 MB limit."}), 413
    return "The upload exceeds the 100 MB limit.", 413


@app.get("/health")
def health():
    return jsonify({"status": "ok", "model_available": MODEL_PATH.is_file()})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=False, threaded=True)
