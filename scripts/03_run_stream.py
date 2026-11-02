import yaml
import cv2
import time
from pathlib import Path
from visionflow.core.tracker_voter import ResolutionAgnosticPipeline

def main():
    with open("configs/pipeline_config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    video_source = cfg["data"]["sample_video"]
    output_dir = Path(cfg["data"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    output_video_path = str(output_dir / "processed_traffic_analytics.mp4")

    pipeline = ResolutionAgnosticPipeline(
        weights_path=cfg["model"]["trained_weights"],
        normalized_counting_line=cfg["analytics"]["counting_line"]
    )

    cap = cv2.VideoCapture(video_source)
    fps_orig = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps_orig, (w, h))
    pcu_weights = cfg["analytics"].get("pcu_weights", {})

    print(f"[*] Đang xử lý luồng video: {video_source} ({w}x{h} @ {fps_orig} FPS)...")
    frame_idx = 0
    t0 = time.perf_counter()

    for annotated_frame, counts_dict in pipeline.process_video_stream(video_source):
        frame_idx += 1
        # Tính tổng chỉ số tải trọng giao thông (PCU)
        total_pcu = sum(count * pcu_weights.get(cls_name, 1.0) for cls_name, count in counts_dict.items())
        elapsed = time.perf_counter() - t0
        current_fps = frame_idx / max(elapsed, 1e-6)

        # Vẽ bảng Dashboard nhỏ gọn lên góc trái trên của video
        overlay_text = f"FPS: {current_fps:.1f} | Total Load: {total_pcu:.1f} PCU | Counts: {counts_dict}"
        cv2.rectangle(annotated_frame, (10, 10), (min(w - 10, 850), 55), (0, 0, 0), -1)
        cv2.putText(annotated_frame, overlay_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 128), 2)

        writer.write(annotated_frame)
        if frame_idx % 100 == 0:
            print(f" -> Đã xử lý {frame_idx} frames | Tốc độ trung bình: {current_fps:.1f} FPS | {counts_dict}")

    writer.release()
    print(f"[+] Hoàn tất! Video kết quả được lưu tại: {output_video_path}")

if __name__ == "__main__":
    main()