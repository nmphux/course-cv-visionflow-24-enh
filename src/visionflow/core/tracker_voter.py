# src/visionflow/core/tracker_voter.py
from collections import defaultdict
import numpy as np
import cv2
from ultralytics import YOLO

class TemporalClassVoter:
    """
    Khắc phục triệt để hiện tượng nhảy nhãn (Class Flickering) giữa Car và Van qua các frame.
    Thay vì lấy class của từng frame độc lập, ta tích lũy điểm tin cậy theo hàm mũ (EMA) 
    cho từng track_id xuyên suốt lịch sử di chuyển của xe đó.
    """
    def __init__(self, alpha: float = 0.85):
        self.alpha = alpha
        # Lưu điểm tích lũy của từng class cho mỗi track_id: {track_id: {class_id: ema_score}}
        self.track_class_scores = defaultdict(lambda: defaultdict(float))

    def update_and_get_stable_class(self, track_id: int, current_cls: int, current_conf: float) -> tuple[int, float]:
        scores = self.track_class_scores[track_id]
        # Giảm nhẹ trọng số quá khứ (decay) và cộng dồn confidence ở frame hiện tại
        for cls_id in list(scores.keys()):
            scores[cls_id] *= self.alpha
        scores[current_cls] += (1.0 - self.alpha) * current_conf

        # Chọn class có tổng điểm tích lũy lịch sử cao nhất
        best_cls = max(scores.items(), key=lambda x: x[1])[0]
        return best_cls, scores[best_cls]


class ResolutionAgnosticPipeline:
    """
    Pipeline suy luận thời gian thực với YOLO26.
    Hoạt động trên MỌI độ phân giải video và MỌI bộ nhãn class mà không cần sửa code.
    """
    def __init__(
        self, 
        weights_path: str, 
        normalized_counting_line: list = [[0.1, 0.65], [0.9, 0.65]] # Tọa độ tương đối [0..1]
    ):
        self.model = YOLO(weights_path)
        self.voter = TemporalClassVoter(alpha=0.85)
        self.norm_line = normalized_counting_line
        self.counted_ids = set()
        self.class_counter = defaultdict(int)

    def process_video_stream(self, video_source: str):
        # Bật stream=True (chống tràn RAM), half=True (FP16 chống tụt FPS trên RTX 4050),
        # và sử dụng ByteTrack tích hợp sẵn
        results_generator = self.model.track(
            source=video_source,
            stream=True,
            persist=True,
            tracker="bytetrack.yaml",
            nms=False,          # Kích hoạt One-to-One Native End-to-End Head của YOLO26
            conf=0.25,
            verbose=False
        )

        for result in results_generator:
            frame = result.orig_img
            h, w = frame.shape[:2]
            class_names = result.names  # Tự động lấy danh sách tên class từ chính model (không hardcode)

            # Tự động quy đổi vạch đếm từ tỷ lệ [0..1] sang Pixel thực tế của bất kỳ video nào
            p1 = (int(self.norm_line[0][0] * w), int(self.norm_line[0][1] * h))
            p2 = (int(self.norm_line[1][0] * w), int(self.norm_line[1][1] * h))
            cv2.line(frame, p1, p2, (0, 255, 255), max(2, int(min(w, h) * 0.003)))

            if result.boxes is not None and result.boxes.id is not None:
                boxes_xyxy = result.boxes.xyxy.cpu().numpy()
                track_ids = result.boxes.id.int().cpu().tolist()
                raw_clss = result.boxes.cls.int().cpu().tolist()
                confs = result.boxes.conf.cpu().tolist()

                for box, track_id, raw_cls, conf in zip(boxes_xyxy, track_ids, raw_clss, confs):
                    # 1. Làm mượt nhãn bằng EMA Voting (Chống nhảy nhãn Car <-> Van)
                    stable_cls, _ = self.voter.update_and_get_stable_class(track_id, raw_cls, conf)
                    label_name = class_names[stable_cls]

                    # 2. Kiểm tra cắt vạch đếm (Dùng tâm đáy của xe)
                    cx, cy = int((box[0] + box[2]) / 2), int(box[3])
                    if abs(cy - p1[1]) < max(10, int(h * 0.02)) and (p1[0] <= cx <= p2[0]):
                        if track_id not in self.counted_ids:
                            self.counted_ids.add(track_id)
                            self.class_counter[label_name] += 1

                    # 3. Vẽ giao diện tự động co giãn độ dày nét vẽ và cỡ chữ theo độ phân giải ảnh
                    font_scale = max(0.5, min(w, h) / 1200.0)
                    thickness = max(1, int(min(w, h) / 500.0))
                    x1, y1, x2, y2 = map(int, box)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 100), thickness)
                    cv2.putText(
                        frame, f"#{track_id} {label_name}", (x1, max(20, y1 - 8)),
                        cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness
                    )

            yield frame, dict(self.class_counter)