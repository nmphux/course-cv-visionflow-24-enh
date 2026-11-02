# src/visionflow/training/trainer.py
import os
import torch
from ultralytics import YOLO
from pathlib import Path
import pandas as pd
import numpy as np
import yaml

# Chống phân mảnh bộ nhớ VRAM trên PyTorch
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

class AdaptiveYOLO26Trainer:
    def __init__(self, model_scale: str = "yolo26s.pt"):
        self.model = YOLO(model_scale)

    @staticmethod
    def _get_hardware_safe_config(num_images: int, rec: dict) -> tuple[int, int]:
        """
        Tự động kiểm tra dung lượng VRAM của GPU hiện tại để chọn imgsz và batch_size
        an toàn tuyệt đối, đồng thời đảm bảo (num_images % batch_size != 1) để không lỗi BatchNorm.
        """
        vram_gb = 4.0
        if torch.cuda.is_available():
            vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)
            torch.cuda.empty_cache()

        # Phân tầng theo dung lượng VRAM thực tế
        if vram_gb <= 6.5:       # Ví dụ: RTX 3050 / RTX 4050 Laptop (6GB VRAM)
            safe_imgsz = 640
            candidates = [12, 10, 8, 6]
        elif vram_gb <= 10.0:    # Ví dụ: RTX 3060 / 4060 / 4070 (8GB VRAM)
            safe_imgsz = 640
            candidates = [16, 24, 12, 8]
        else:                    # GPU Server (T4 16GB, A100, RTX 3090/4090)
            safe_imgsz = rec["imgsz"]
            candidates = [32, 24, 16, 12, 8]

        # Chọn batch_size sao cho batch cuối không bao giờ dư đúng 1 ảnh (185 % 6 = 5 ảnh -> Rất đẹp!)
        for b in candidates:
            if b < num_images and (num_images % b != 1):
                return safe_imgsz, b
        return safe_imgsz, 4

    def train_adaptive(self, data_yaml: str, profile_report: dict, epochs: int = 50):
        # rec = profile_report.get("recommended_hyperparams", {
        #     "copy_paste": 0.2, "mixup": 0.15, "close_mosaic": 15
        # })
        rec = profile_report["recommended_hyperparams"]

        yaml_path = Path(data_yaml).resolve()
        with open(yaml_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        train_img_dir = (yaml_path.parent / cfg['train']).resolve()
        num_imgs = len(list(train_img_dir.glob("*.*")))
        
        # Tự động lấy imgsz=640 và batch=6 (với 185 ảnh: 185 = 30 * 6 + 5) cho RTX 4050 6GB
        safe_imgsz, safe_batch = self._get_hardware_safe_config(num_imgs, rec)
        print(f"[*] Cấu hình tự thích ứng phần cứng: imgsz={safe_imgsz}, batch={safe_batch} (Tổng {num_imgs} ảnh, dư {num_imgs % safe_batch} ở batch cuối)")

        results = self.model.train(
            data=str(yaml_path),
            epochs=epochs,
            imgsz=safe_imgsz,                # Khóa ở 640 cho GPU 6GB VRAM
            batch=safe_batch,                # batch=6 chỉ tốn ~2.4GB VRAM (trong notebook cũ batch=8 tốn 3.22GB)
            cache="ram",                     # Đọc 185 ảnh trong 1.1 giây từ RAM cực nhanh!
            optimizer="MuSGD",
            cos_lr=True,
            
            # --- TỔNG QUÁT HÓA CHỐNG GÁN NHẦM CAR <-> VAN ---
            dropout=0.15,
            mixup=rec.get("mixup", 0.15),
            cutmix=0.15,
            copy_paste=rec.get("copy_paste", 0.3),
            
            # --- ĐA TỶ LỆ NHẸ NHÀNG CHO 6GB VRAM ---
            multi_scale=0.15,                # Co giãn nhẹ +/- 15% (544px -> 736px), cực kỳ an toàn cho 6GB VRAM
            close_mosaic=rec.get("close_mosaic", 15),
            amp=True,
            exist_ok=True,
            workers=2                        # Giảm workers xuống 2 vì ảnh đã nằm sẵn trong RAM (cache="ram")
        )
        return results

def find_mislabelled_boxes(
        self, 
        data_yaml: str, 
        best_weights: str, 
        conf_thresh: float = 0.80,
        auto_overwrite: bool = False
    ) -> pd.DataFrame:
        """
        Dùng model đã học tổng quát để bắt lỗi các nhãn gán tay bị nhầm (ví dụ: car <-> van).
        - Nếu auto_overwrite=False: Chỉ xuất danh sách nghi ngờ ra CSV.
        - Nếu auto_overwrite=True: Tự động sửa lại class_id trong file .txt theo gợi ý của model.
        """
        detector = YOLO(best_weights)
        yaml_path = Path(data_yaml).resolve()
        with open(yaml_path, 'r', encoding='utf-8') as f:
            cfg = yaml.safe_load(f)
        
        train_img_dir = (yaml_path.parent / cfg['train']).resolve()
        if train_img_dir.name == 'images':
            train_label_dir = train_img_dir.parent / 'labels'
        else:
            train_label_dir = yaml_path.parent / cfg['train'].replace('images', 'labels')

        suspicious_records = []
        from visionflow.data_engine.label_sanitizer import UniversalDatasetSanitizer

        for res in detector.predict(source=str(train_img_dir), stream=True, conf=conf_thresh, verbose=False):
            img_path = Path(res.path)
            label_path = train_label_dir / f"{img_path.stem}.txt"
            if not label_path.exists():
                continue

            gt_lines = label_path.read_text(encoding='utf-8').strip().splitlines()
            pred_boxes = res.boxes
            new_gt_lines = []
            file_modified = False

            for line in gt_lines:
                parts = list(map(float, line.split()))
                if len(parts) < 5:
                    continue
                gt_cls = int(parts[0])
                gt_xywhn = np.array(parts[1:5])
                final_cls = gt_cls

                for pbox in pred_boxes:
                    pred_cls = int(pbox.cls.item())
                    pred_conf = float(pbox.conf.item())
                    pred_xywhn = pbox.xywhn[0].cpu().numpy()

                    iou = UniversalDatasetSanitizer._compute_iou_xywhn(gt_xywhn, pred_xywhn)
                    if iou > 0.75 and gt_cls != pred_cls:
                        names = cfg['names']
                        suspicious_records.append({
                            "image_file": img_path.name,
                            "manual_label": names[gt_cls] if isinstance(names, list) else names.get(gt_cls, gt_cls),
                            "model_suggested_label": names[pred_cls] if isinstance(names, list) else names.get(pred_cls, pred_cls),
                            "model_confidence": round(pred_conf, 3),
                            "iou_overlap": round(iou, 3),
                            "action_taken": "OVERWRITTEN" if auto_overwrite else "FLAGGED_ONLY"
                        })
                        if auto_overwrite:
                            final_cls = pred_cls
                            file_modified = True
                        break

                new_gt_lines.append(f"{final_cls} {parts[1]:.6f} {parts[2]:.6f} {parts[3]:.6f} {parts[4]:.6f}")

            if auto_overwrite and file_modified:
                label_path.write_text("\n".join(new_gt_lines) + "\n", encoding='utf-8')

        df = pd.DataFrame(suspicious_records)
        output_csv = yaml_path.parent.parent.parent / "outputs" / "mislabelled_review_list.csv"
        output_csv.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_csv, index=False)
        return df