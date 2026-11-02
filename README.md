<p align="center">
  <img src="src/visionflow/api/static/img/logo_option_a.jpg" alt="VisionFlow Logo" width="140" style="border-radius: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.35);" />
</p>

# VisionFlow: Dataset-Agnostic Real-Time Traffic Analytics Engine

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.10+"></a>
  <a href="https://pytorch.org/"><img src="https://img.shields.io/badge/PyTorch-2.6%2Bcu124-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch 2.6"></a>
  <a href="https://docs.ultralytics.com/"><img src="https://img.shields.io/badge/YOLO-YOLO26-purple?style=for-the-badge" alt="YOLO26"></a>
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-WSL2%20Pass--through-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License: MIT"></a>
</p>

<p align="center">
  <strong>Language:</strong>
  <a href="#english">English</a> |
  <a href="#tiếng-việt">Tiếng Việt</a>
</p>

---

<a name="english"></a>

## 🌐 English

### Overview

**VisionFlow** is an enterprise-ready, real-time vehicle analytics and urban traffic monitoring engine powered by **YOLO26**. Moving beyond conventional computer vision demos that merely plot bounding boxes, VisionFlow addresses core production bottlenecks: **eliminating class ambiguity between visually identical vehicle categories (such as Car vs. Van), applying Data-Centric AI dataset sanitation, and remaining fully resolution- and dataset-agnostic without modifying source code.**

The platform ships with a built-in **Operations Web Console** that provides live RTSP/USB camera feeds, multi-camera stream processing, an on-demand inference laboratory, and bilingual telemetry (EN/VI).

---

### 🌟 Key Technical Innovations

- **YOLO26 Native End-to-End (`nms=False`):** Bypasses conventional Non-Maximum Suppression (NMS) layers, minimizing post-processing latency and maximizing modern GPU Tensor Core utilization.
- **Dataset-Agnostic Sanitizer:** Automatically audits YOLO dataset structures, removes corrupt coordinates, resolves manual double-annotation conflicts ($IoU > 0.85$), and generates clean data profiles.
- **Confident Learning Label Audit:** Employs spatial probabilistic scoring to automatically identify and export mislabelled ground-truth boxes (e.g., human annotator confusion between `car` and `van`) when model confidence reaches $\ge 80\%$.
- **Temporal Class Voting (EMA Smoothing):** Eliminates frame-to-frame class flickering by computing Exponential Moving Average confidence scores over unique ByteTrack tracking identities (`track_id`).
- **Urban Passenger Car Unit (PCU) Analytics:** Converts raw vehicle volumes into dynamic road capacity strain indices (`motorcycle: 0.3`, `car: 1.0`, `van: 1.4`, `bus/truck: 2.5 PCU`) rather than simplistic vehicle counts.
- **Normalized Spatial Coordinates:** Counting lines, spatial boundaries, and visual telemetry scale across relative ratios $[0.0, 1.0]$, seamlessly adjusting from 360p up to 4K streams.

---

### 📊 Benchmark & Performance

Evaluated on an **NVIDIA GeForce RTX 4050 Laptop GPU (6GB VRAM)** via Docker container with CUDA 12.4 pass-through:

| Pipeline Architecture                      |    Resolution    | Batch Size |          Latency          |     Throughput     | VRAM Footprint |
| :----------------------------------------- | :--------------: | :--------: | :-----------------------: | :----------------: | :------------: |
| **Baseline (YOLOv10s FP32 + Flask)**       | $384 \times 640$ |     1      |  $25.0 - 47.3\text{ ms}$  |    ~25 - 40 FPS    |    ~3.2 GB     |
| **VisionFlow (YOLO26s MuSGD + ByteTrack)** | $640 \times 640$ |  6 (Safe)  | **$8.2 - 9.1\text{ ms}$** | **~110 - 120 FPS** |  **~2.4 GB**   |

> **Memory Resilience Note:** The internal `AdaptiveYOLO26Trainer` automatically computes safe batches ($N \pmod B \ne 1$) to prevent mathematical variance divergence in `BatchNorm2d`. In-memory caching (`cache="ram"`) accelerates training I/O from 4.3 MB/s to over 150 it/s.

---

### 🏗️ Project Architecture

```text
visionflow-yolo26/
├── configs/
│   └── pipeline_config.yaml         # Central pipeline configuration
├── data/
│   ├── datasets/                    # YOLO formatted datasets (e.g. scratch-vehdet-1k)
│   ├── samples/                     # Test videos and images
│   └── outputs/                     # Generated videos, reports, and review CSVs
├── deploy/
│   └── docker/
│       └── Dockerfile               # CUDA 12.4 + PyTorch 2.6 runtime image
├── scripts/
│   ├── 01_sanitize_and_profile.py   # Dataset sanitization & distribution profiler
│   ├── 02_train_and_export.py       # Adaptive training & label audit execution
│   └── 03_run_stream.py             # Headless stream/video analytics runner
├── src/
│   └── visionflow/
│       ├── core/                    # Tracker voter, EMA smoothing, and detector
│       ├── data_engine/             # Universal label sanitizer & profiler
│       ├── training/                # Adaptive trainer with hardware-safe batch logic
│       ├── analytics/               # Spatial metrics & congestion indices
│       └── api/                     # Flask Operations Console & CameraManager
├── docker-compose.yaml              # Single-command GPU container deployment
├── pyproject.toml                   # Standard PEP 621 package specification
└── README.md
```

---

### 🚀 Quick Start Guide

#### Option 1: Docker (Recommended)

**Prerequisites:** Docker Desktop installed with NVIDIA Container Toolkit (WSL 2 on Windows or Linux native).

1. **Build and start the container with GPU pass-through:**

   ```bash
   docker compose build
   docker compose run --rm -p 8000:8000 traffic-engine
   ```

2. **Execute Pipeline Steps inside container:**

   ```bash
   # Step 1: Clean corrupt labels & profile dataset
   python3 scripts/01_sanitize_and_profile.py

   # Step 2: Run adaptive training with label audit
   python3 scripts/02_train_and_export.py

   # Step 3: Launch Web Operations Console
   python3 -m visionflow.api.app
   ```

   Open your browser at: `http://localhost:8000`

---

#### Option 2: Native Local Environment

**Prerequisites:** Python 3.10+, CUDA 12.4 compatible driver (optional, falls back to CPU).

1. **Create and activate virtual environment:**

   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   ```bash
   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install PyTorch with CUDA 12.4 and VisionFlow in editable mode:**

   ```bash
   python -m pip install --upgrade pip
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
   pip install -e .
   ```

3. **Start the Web Operations Console directly:**

   ```bash
   python -m visionflow.api.app
   ```

   Access the web application at [http://127.0.0.1:8000](http://127.0.0.1:8000).

4. **Run batch video stream analytics (Headless CLI):**
   ```bash
   python scripts/03_run_stream.py
   ```
   Annotated results and real-time PCU telemetry will be written to `data/outputs/processed_traffic_analytics.mp4`.

---

### ⚙️ Pipeline Configuration

All operations are controlled via [`configs/pipeline_config.yaml`](configs/pipeline_config.yaml):

```yaml
project_name: "visionflow_traffic"

data:
  dataset_yaml: "data/datasets/scratch-vehdet-1k/data.yaml"
  sample_video: "data/samples/0621_highway.mp4"
  output_dir: "data/outputs"
  label_audit:
    enabled: false # Set true to flag suspicious manual labels
    conf_threshold: 0.80 # Minimum confidence required to challenge ground truth
    auto_overwrite_labels: false # Automatically overwrite suspicious .txt annotations

model:
  base_weights: "yolo26s.pt"
  trained_weights: "weights/best.pt"
  epochs: 80
  conf_threshold: 0.25

analytics:
  counting_line: [[0.05, 0.65], [0.95, 0.65]] # Normalized relative coordinates [0..1]
  ema_smoothing_alpha: 0.85 # Smoothing factor for TemporalClassVoter
  pcu_weights:
    motobike: 0.3
    car: 1.0
    van: 1.4
    bus: 2.5
    truck: 2.5
```

---

<a name="tiếng-việt"></a>

## 🇻🇳 Tiếng Việt

### Giới Thiệu

**VisionFlow** là hệ thống giám sát và phân tích tải trọng giao thông đô thị theo thời gian thực thế hệ mới, ứng dụng kiến trúc **YOLO26**. Vượt trên các mô hình thị giác máy tính truyền thống chỉ dừng lại ở việc vẽ bounding box, VisionFlow giải quyết triệt để các bài toán thực tiễn: **khử hiện tượng nhảy nhãn giữa các dòng xe tương đồng (Car vs. Van), quy trình làm sạch dữ liệu tự động (Data-Centric AI), và thích ứng linh hoạt với mọi độ phân giải camera/tập dữ liệu mà không cần sửa mã nguồn.**

Hệ thống tích hợp sẵn **Web Operations Console** hỗ trợ quản lý camera USB/RTSP trực tiếp, xử lý suy luận video/ảnh theo yêu cầu và giao diện song ngữ Anh - Việt.

---

### 🌟 Điểm Nhấn Kỹ Thuật

- **YOLO26 Native End-to-End (`nms=False`):** Loại bỏ hoàn toàn bước Non-Maximum Suppression (NMS) truyền thống, giảm độ trễ hậu xử lý và tận dụng tối đa nhân Tensor Cores trên GPU thế hệ mới.
- **Bộ Làm Sạch Dữ Liệu Tự Động (Dataset-Agnostic Sanitizer):** Tự động phát hiện và loại bỏ box lỗi hình học, khử trùng lặp do vẽ đè tay ($IoU > 0.85$) và sinh hồ sơ phân phối nhãn dataset.
- **Kiểm Định Nhãn Nhiễu (Confident Learning Audit):** Đánh giá phân phối xác suất để phát hiện các trường hợp gán nhầm nhãn giữa `car` và `van` khi độ tự tin mô hình đạt $\ge 80\%$, xuất báo cáo CSV chi tiết.
- **Làm Mượt Nhãn Theo Thời Gian (Temporal Class Voting EMA):** Triệt tiêu hiện tượng nhấp nháy nhãn (Class Flickering) qua từng khung hình bằng cách tích lũy trọng số lịch sử nhận diện theo từng `track_id` duy nhất qua thuật toán ByteTrack.
- **Chỉ Số Tải Trọng Đô Thị (PCU - Passenger Car Unit):** Quy đổi lưu lượng phương tiện ra áp lực mặt đường thực tế (`xe máy: 0.3`, `xe con: 1.0`, `xe van: 1.4`, `xe buýt/xe tải: 2.5 PCU`) thay vì chỉ đếm số đầu xe đơn thuần.
- **Tọa Độ Chuẩn Hóa Linh Hoạt:** Toàn bộ vạch đếm và vùng giám sát tính toán theo tỷ lệ tương đối $[0.0, 1.0]$, tự co giãn chuẩn xác trên mọi độ phân giải từ 360p, 720p, 1080p đến 4K.

---

### 📊 Kết Quả Thực Nghiệm

Thử nghiệm trên phần cứng **NVIDIA GeForce RTX 4050 Laptop GPU (6GB VRAM)** qua Docker container (WSL 2):

| Cấu Hình Pipeline                          |  Kích Thước Ảnh  | Batch Size |     Độ Trễ (Latency)      |    Tốc Độ (FPS)    | VRAM Chiếm Dụng |
| :----------------------------------------- | :--------------: | :--------: | :-----------------------: | :----------------: | :-------------: |
| **Bản Gốc (YOLOv10s FP32 + Flask)**        | $384 \times 640$ |     1      |  $25.0 - 47.3\text{ ms}$  |    ~25 - 40 FPS    |     ~3.2 GB     |
| **VisionFlow (YOLO26s MuSGD + ByteTrack)** | $640 \times 640$ |  6 (Safe)  | **$8.2 - 9.1\text{ ms}$** | **~110 - 120 FPS** |   **~2.4 GB**   |

> **Tối ưu hóa bộ nhớ:** Thuật toán `AdaptiveYOLO26Trainer` tự động tính toán batch an toàn ($N \pmod B \ne 1$) nhằm loại trừ lỗi phân kỳ trong `BatchNorm2d`. Cơ chế `cache="ram"` tăng tốc độ đọc dữ liệu từ 4.3 MB/s lên hơn 150 it/s.

---

### 🚀 Hướng Dẫn Vận Hành Nhanh

#### Cách 1: Vận hành với Docker (Khuyên dùng)

**Yêu cầu:** Máy đã cài đặt Docker Desktop và kích hoạt NVIDIA Container Toolkit.

1. **Khởi dựng container có GPU pass-through:**

   ```bash
   docker compose build
   docker compose run --rm -p 8000:8000 traffic-engine
   ```

2. **Chạy các tác vụ bên trong container:**

   ```bash
   # Bước 1: Quét dọn nhãn lỗi & thống kê dataset
   python3 scripts/01_sanitize_and_profile.py

   # Bước 2: Huấn luyện thích ứng & kiểm định nhãn
   python3 scripts/02_train_and_export.py

   # Bước 3: Khởi chạy Web Console trực tiếp
   python3 -m visionflow.api.app
   ```

   Truy cập trên trình duyệt: `http://localhost:8000`

---

#### Cách 2: Vận hành trực tiếp trên máy cục bộ (Local)

1. **Tạo và kích hoạt môi trường ảo Python (Python 3.10+):**

   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   ```bash
   # Linux / macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Cài đặt thư viện với CUDA 12.4:**

   ```bash
   python -m pip install --upgrade pip
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu124
   pip install -e .
   ```

3. **Khởi chạy Web Operations Console trực tiếp:**

   ```bash
   python -m visionflow.api.app
   ```

   Mở trình duyệt truy cập: [http://127.0.0.1:8000](http://127.0.0.1:8000).

4. **Chạy phân tích video chế độ CLI (không cần giao diện):**
   ```bash
   python scripts/03_run_stream.py
   ```
   Video đầu ra kèm telemetry PCU sẽ được lưu tại `data/outputs/processed_traffic_analytics.mp4`.

---

## 📄 License

Dự án phát hành theo giấy phép [MIT License](LICENSE).
