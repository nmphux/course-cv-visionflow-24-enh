# Sử dụng base image chuẩn của NVIDIA chứa sẵn CUDA 12.4 và cuDNN 9
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

# Chặn tương tác hỏi giờ/vùng trong quá trình cài đặt
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Cài đặt Python 3.10 và các thư viện hệ thống cần thiết cho OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    python3-dev \
    ffmpeg \
    libsm6 \
    libxext6 \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Nâng cấp pip và cài đặt PyTorch CUDA
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir torch torchvision --index-url https://download.pytorch.org/whl/cu124

# Copy cấu hình package và cài đặt
COPY pyproject.toml .
COPY src/ src/
RUN pip3 install --no-cache-dir -e .

# Thư mục làm việc mặc định
CMD ["bash"]