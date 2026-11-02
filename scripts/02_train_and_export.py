# scripts/02_train_and_export.py
import argparse
import yaml
import json
import shutil
from pathlib import Path
from visionflow.training.trainer import AdaptiveYOLO26Trainer

def parse_args():
    parser = argparse.ArgumentParser(description="Train YOLO26 & Optional Label Auditing")
    # Cho phép ghi đè nhanh bằng dòng lệnh nếu không muốn mở file YAML
    parser.add_argument(
        "--audit-labels", 
        dest="audit_labels", 
        action="store_true", 
        help="Bật chế độ nghi ngờ và rà soát nhãn gán nhầm"
    )
    parser.add_argument(
        "--no-audit-labels", 
        dest="audit_labels", 
        action="store_false", 
        help="Tắt chế độ nghi ngờ nhãn (tin tưởng 100% nhãn gốc)"
    )
    parser.set_defaults(audit_labels=None)
    return parser.parse_args()

def main():
    args = parse_args()
    with open("configs/pipeline_config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    profile_path = Path(cfg['data']['output_dir']) / "dataset_profile.json"
    profile_report = {}
    if profile_path.exists():
        with open(profile_path, "r", encoding="utf-8") as f:
            profile_report = json.load(f)

    trainer = AdaptiveYOLO26Trainer(model_scale=cfg["model"]["base_weights"])
    
    # 1. Huấn luyện mô hình
    print("[*] Bắt đầu huấn luyện mô hình...")
    results = trainer.train_adaptive(
        data_yaml=cfg["data"]["dataset_yaml"],
        profile_report=profile_report,
        epochs=cfg["model"]["epochs"]
    )

    # 2. Copy trọng số tốt nhất về weights/best.pt
    best_run_weight = Path(results.save_dir) / "weights" / "best.pt"
    target_weight = Path(cfg["model"]["trained_weights"])
    target_weight.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(best_run_weight, target_weight)
    print(f"[+] Đã lưu trọng số chuẩn tại: {target_weight}")

    # 3. Kiểm tra Flag bật/tắt việc "cãi" nhãn người dùng
    audit_cfg = cfg["data"].get("label_audit", {})
    # Ưu tiên flag từ CLI (nếu có gõ), nếu không thì lấy trong pipeline_config.yaml
    should_audit = args.audit_labels if args.audit_labels is not None else audit_cfg.get("enabled", True)

    if should_audit:
        conf_thresh = audit_cfg.get("conf_threshold", 0.80)
        auto_overwrite = audit_cfg.get("auto_overwrite_labels", False)
        print(f"[*] [LABEL AUDIT: ON] Đang quét tìm các box gán nhầm (conf >= {conf_thresh}, auto_overwrite={auto_overwrite})...")
        
        df_mislabelled = trainer.find_mislabelled_boxes(
            data_yaml=cfg["data"]["dataset_yaml"],
            best_weights=str(target_weight),
            conf_thresh=conf_thresh,
            auto_overwrite=auto_overwrite
        )
        print(f"[+] Phát hiện {len(df_mislabelled)} box nghi ngờ gán nhầm! Chi tiết lưu tại data/outputs/mislabelled_review_list.csv")
    else:
        print("[*] [LABEL AUDIT: OFF] Bỏ qua bước kiểm tra nhãn gán nhầm (Giữ nguyên 100% nhãn gốc).")

if __name__ == "__main__":
    main()