import yaml
import json
from visionflow.data_engine.label_sanitizer import UniversalDatasetSanitizer

def main():
    with open("configs/pipeline_config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    dataset_yaml = cfg["data"]["dataset_yaml"]
    print(f"[*] Đang quét và làm sạch nhãn tại: {dataset_yaml}")

    sanitizer = UniversalDatasetSanitizer(
        data_yaml_path=dataset_yaml,
        iou_conflict_threshold=cfg["data"]["iou_conflict_threshold"]
    )
    
    train_report = sanitizer.sanitize_and_profile(split="train")
    val_report = sanitizer.sanitize_and_profile(split="val")

    # Lưu hồ sơ dataset ra thư mục data/outputs để phục vụ bước Train
    report_path = f"{cfg['data']['output_dir']}/dataset_profile.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(train_report, f, indent=4)

    print("[+] Hoàn tất làm sạch dữ liệu! Báo cáo chi tiết:")
    print(json.dumps(train_report, indent=4))

if __name__ == "__main__":
    main()