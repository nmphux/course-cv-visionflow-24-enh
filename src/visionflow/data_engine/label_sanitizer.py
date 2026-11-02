# src/visionflow/data_engine/label_sanitizer.py
from pathlib import Path
import yaml
import numpy as np
import cv2
from collections import Counter
from typing import Dict, List, Tuple

class UniversalDatasetSanitizer:
    """
    Tự động đọc bất kỳ bộ dataset chuẩn YOLO nào, bất kể số lượng class hay kích thước ảnh.
    Thực hiện:
    1. Lọc bỏ các box lỗi (ngoài biên, diện tích quá nhỏ < 0.01% ảnh).
    2. Phát hiện xung đột nhãn gán tay (2 box đè lên nhau với IoU > 0.85 trên cùng 1 vật thể).
    3. Phân tích phân phối class & độ phân giải để tự động cấu hình YOLO26.
    """
    def __init__(self, data_yaml_path: str, iou_conflict_threshold: float = 0.85):
        self.yaml_path = Path(data_yaml_path)
        with open(self.yaml_path, 'r', encoding='utf-8') as f:
            self.data_cfg = yaml.safe_load(f)
        
        self.class_names = self.data_cfg.get('names', {})
        if isinstance(self.class_names, list):
            self.class_names = {i: name for i, name in enumerate(self.class_names)}
        self.iou_thresh = iou_conflict_threshold

    @staticmethod
    def _compute_iou_xywhn(box1: np.ndarray, box2: np.ndarray) -> float:
        """Tính IoU giữa 2 box ở định dạng normalized [x_center, y_center, w, h]."""
        b1_x1, b1_y1 = box1[0] - box1[2] / 2, box1[1] - box1[3] / 2
        b1_x2, b1_y2 = box1[0] + box1[2] / 2, box1[1] + box1[3] / 2
        b2_x1, b2_y1 = box2[0] - box2[2] / 2, box2[1] - box2[3] / 2
        b2_x2, b2_y2 = box2[0] + box2[2] / 2, box2[1] + box2[3] / 2

        inter_x1, inter_y1 = max(b1_x1, b2_x1), max(b1_y1, b2_y1)
        inter_x2, inter_y2 = min(b1_x2, b2_x2), min(b1_y2, b2_y2)
        inter_area = max(0.0, inter_x2 - inter_x1) * max(0.0, inter_y2 - inter_y1)

        area1, area2 = box1[2] * box1[3], box2[2] * box2[3]
        return inter_area / (area1 + area2 - inter_area + 1e-6)

    def sanitize_and_profile(self, split: str = 'train', filter_overlaps: bool = False) -> Dict:
        """Quét toàn bộ thư mục nhãn, sửa lỗi tại chỗ và trả về hồ sơ thống kê của Dataset."""
        img_dir = (self.yaml_path.parent / self.data_cfg[split]).resolve()
        label_dir = img_dir.parent / 'labels' if 'images' in str(img_dir) else img_dir

        class_counts = Counter()
        aspect_ratios = []
        small_objects_ratio = 0
        total_boxes = 0
        removed_corrupt_boxes = 0
        resolved_overlapping_boxes = 0

        for txt_file in label_dir.glob("*.txt"):
            lines = txt_file.read_text(encoding='utf-8').strip().splitlines()
            valid_boxes = []

            for line in lines:
                parts = list(map(float, line.strip().split()))
                if len(parts) != 5:
                    continue
                cls_id, xc, yc, w, h = int(parts[0]), parts[1], parts[2], parts[3], parts[4]

                # 1. Cắt biên chuẩn hóa về [0.0, 1.0] và loại bỏ box chấm nhầm (quá nhỏ)
                xc, yc = np.clip(xc, 0.0, 1.0), np.clip(yc, 0.0, 1.0)
                w, h = np.clip(w, 0.0, 1.0), np.clip(h, 0.0, 1.0)
                if w * h < 1e-4 or w <= 0.002 or h <= 0.002:
                    removed_corrupt_boxes += 1
                    continue
                valid_boxes.append([cls_id, xc, yc, w, h])

            # # 2. Khử box vẽ đè lên nhau (do gán tay nhầm 2 lần trên 1 xe)
            if (filter_overlaps):
                keep_indices = []
                for i in range(len(valid_boxes)):
                    keep = True
                    for j in keep_indices:
                        iou = self._compute_iou_xywhn(np.array(valid_boxes[i][1:]), np.array(valid_boxes[j][1:]))
                        if iou > self.iou_thresh:
                            keep = False
                            resolved_overlapping_boxes += 1
                            break
                    if keep:
                        keep_indices.append(i)

                cleaned_boxes = [valid_boxes[idx] for idx in keep_indices]
            else: cleaned_boxes = valid_boxes

            # Ghi đè lại file nhãn sạch
            with open(txt_file, 'w', encoding='utf-8') as f:
                for b in cleaned_boxes:
                    f.write(f"{b[0]} {b[1]:.6f} {b[2]:.6f} {b[3]:.6f} {b[4]:.6f}\n")
                    class_counts[b[0]] += 1
                    total_boxes += 1
                    if b[3] * b[4] < (32 * 32) / (640 * 640):  # Vật thể nhỏ chuẩn COCO
                        small_objects_ratio += 1

        # 3. Tự động tính toán cấu hình tối ưu cho Dataset này
        counts = list(class_counts.values())
        imbalance_ratio = max(counts) / max(1, min(counts)) if counts else 1.0
        small_obj_pct = (small_objects_ratio / max(1, total_boxes)) * 100

        return {
            "num_classes": len(self.class_names),
            "class_distribution": {self.class_names.get(k, k): v for k, v in class_counts.items()},
            "imbalance_ratio": round(imbalance_ratio, 2),
            "small_object_percentage": round(small_obj_pct, 2),
            "removed_corrupt_boxes": removed_corrupt_boxes,
            "resolved_overlapping_boxes": resolved_overlapping_boxes,
            # Tự động bật Copy-Paste & tăng độ phân giải nếu phát hiện lệch class hoặc nhiều vật thể nhỏ
            "recommended_hyperparams": {
                "imgsz": 960 if small_obj_pct > 35.0 else 640,
                "copy_paste": 0.4 if imbalance_ratio > 10.0 else 0.1,
                "mixup": 0.15 if imbalance_ratio > 5.0 else 0.0,
                "close_mosaic": 15
            }
        }