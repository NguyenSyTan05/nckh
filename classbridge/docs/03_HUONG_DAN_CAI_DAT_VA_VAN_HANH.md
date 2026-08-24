# 03. Hướng Dẫn Cài Đặt & Vận Hành (Setup & Operation Guide)

---

## 1. Yêu Cầu Hệ Thống (Prerequisites)

### 1.1. Phần Cứng Đề Xuất
- **GPU (Khuyên dùng cho Real-Time)**: NVIDIA GPU với tối thiểu **4GB VRAM** (ví dụ RTX 3050, RTX 3060, T4, A100...). Đã cài đặt NVIDIA Driver & CUDA 12.x.
- **CPU Mode (Dự phòng)**: CPU đa nhân (tối thiểu 4 cores, khuyến nghị 8 cores), RAM tối thiểu 8GB.

### 1.2. Môi Trường Phần Mềm
- **Hệ điều hành**: Windows 10/11 (64-bit) hoặc Linux (Ubuntu 22.04+).
- **Python**: Phiên bản `3.11.x` hoặc `3.10.x`.
- **Node.js**: Phiên bản `>= 22.13.0` kèm theo `npm`.
- **PowerShell** (đối với môi trường Windows).

---

## 2. Cài Đặt Môi Trường

### 2.1. Cài Đặt Phân Hệ Frontend Web
Từ thư mục gốc dự án:
```powershell
cd classbridge/frontend
npm install
```

### 2.2. Cài Đặt Phân Hệ AI Service & Python Venv
Từ thư mục gốc dự án:
```powershell
cd classbridge/backend/ai-service
python -m venv .venv
# Kích hoạt venv trên Windows:
.venv\Scripts\activate
# Cài đặt thư viện:
pip install -r requirements.txt
```

Hoặc sử dụng script cài đặt tự động toàn bộ dependencies AI:
```powershell
powershell -ExecutionPolicy Bypass -File classbridge/training/install_ai_deps.ps1
```

---

## 3. Cấu Hình Biến Môi Trường (Environment Variables)

Các biến môi trường có thể được cấu hình linh hoạt trong file `.env` hoặc truyền trực tiếp qua PowerShell:

| Biến Môi Trường | Giá Trị Mặc Định | Ý Nghĩa / Tùy Chọn |
|---|---|---|
| `WHISPER_DEVICE` | `cuda` (nếu có) / `cpu` | Thiết bị chạy suy luận Whisper (`cuda`, `cpu`) |
| `WHISPER_COMPUTE_TYPE` | `int8_float16` / `int8` | Định dạng lượng tử hóa (`int8`, `float16`, `int8_float16`) |
| `WHISPER_MODEL` | `whisper-large-v3-turbo-ct2` | Đường dẫn thư mục mô hình CT2 chính |
| `WHISPER_CPU_THREADS` | `8` | Số luồng CPU dùng cho giải mã ASR |
| `WHISPER_BEAM_SIZE` | `1` | Kích thước Beam Search (1 = Greedy decoding cho độ trễ thấp) |
| `STREAM_UPDATE_SECONDS`| `0.3` | Chu kỳ cập nhật phụ đề realtime (giây) |
| `STREAM_ROLLING_SECONDS`| `8` | Độ dài cửa sổ đệm âm thanh cuốn chiếu (giây) |
| `TRANSLATION_CPU_THREADS`| `4` | Số luồng CPU cấp cho NMT translation |
| `TRANSLATION_USE_ENSEMBLE`| `true` | Sử dụng mô hình dịch thuật kết hợp |

---

## 4. Hướng Dẫn Khởi Chạy Hệ Thống

### 4.1. Cách 1: Khởi Chạy Master Điều Khiển (Khuyên Dùng)
Hệ thống cung cấp file điều khiển trung tâm hỗ trợ menu trực quan:

```powershell
# Chạy trực tiếp qua NPM:
npm run dev
# hoặc chạy qua PowerShell:
powershell -ExecutionPolicy Bypass -Command "& ./classbridge/start-classbridge.ps1"
```

Menu điều khiển sẽ xuất hiện:
```text
=========================================================================
         CLASSBRIDGE AI - UNIFIED MASTER CONTROL SYSTEM                  
=========================================================================
 Lua chon che do chay:
   [1] Chay Toan Bo Ung Dung ClassBridge (Web App + AI Service)
   [2] Kich hoat Trinh Train AI & Danh Gia Mo Hinh (Train Master Manager)
   [3] Train Giong Noi Ca Nhan (Thu am & Fine-tune 15 cau truc tiep)
   [4] Train Da Giong Vung Mien & Tieng Anh Giong Viet (Multi-Accent ASR)
   [5] Train Whisper Nang Cao DTU (LoRA r=32 + DTU Academic Vocab)
   [6] Thu du lieu nguoi Viet noi tieng Anh (Teacher + Support)
   [0] Thoat
=========================================================================
```
Nhập **`1`** để khởi chạy đồng thời cả **AI Service (Port 8000)** và **Web App (Port 3000)**.

### 4.2. Cách 2: Khởi Chạy Từng Phân Hệ Độc Lập

**Khởi chạy AI Service:**
```powershell
cd classbridge/backend/ai-service
.venv\Scripts\activate
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

**Khởi chạy Frontend Web Client:**
```powershell
cd classbridge/frontend
npm run dev:web
```

---

## 5. Kiểm Tra Hoạt Động (Healthcheck & Logs)

- **Trang chủ Web App**: Truy cập `http://localhost:3000`
- **Kiểm tra trạng thái AI Service**: `GET http://localhost:8000/health`
- **Tài liệu Swagger API**: `http://localhost:8000/docs`
- **File Logs giám sát**:
  - AI Service Logs: `classbridge/backend/ai-service/runtime-supervised-ai.out.log` và `runtime-supervised-ai.err.log`
  - Web App Logs: `classbridge/frontend/runtime-supervised-web.out.log` và `runtime-supervised-web.err.log`
