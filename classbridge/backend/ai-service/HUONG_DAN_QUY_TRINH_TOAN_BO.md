# 📘 TÀI LIỆU HƯỚNG DẪN QUY TRÌNH HỆ THỐNG 2-MODULE (CLASSBRIDGE)
> **Tác giả:** Đồ án Nghiên cứu Khoa học / Đồ án Tốt nghiệp  
> **Cập nhật:** 2026  
> **Mục tiêu:** Hướng dẫn chi tiết cách lưu dữ liệu, sửa dữ liệu, quy trình huấn luyện, xuất mô hình và kiểm thử hệ thống nhận dạng giọng nói & dịch thuật 2-Module độc lập.

---

## 📑 MỤC LỤC
1. [Tổng Quan Kiến Trúc Hệ Thống](#1-tổng-quan-kiến-trúc-hệ-thống)
2. [Cấu Trúc Thư Mục & Cách Lưu Dữ Liệu](#2-cấu-trúc-thư-mục--cách-lưu-dữ-liệu)
3. [Cách Chỉnh Sửa / Thêm Mới Dữ Liệu Huấn Luyện](#3-cách-chỉnh-sửa--thêm-mới-dữ-liệu-huấn-luyện)
4. [Quy Trình 4 Bước Huấn Luyện Từ A Đến Z](#4-quy-trình-4-bước-huấn-luyện-từ-a-đến-z)
   - [A. Module Chuyên Gia Tiếng Việt](#a-module-chuyên-gia-tiếng-việt-module-1)
   - [B. Module Chuyên Gia Tiếng Anh & Accent](#b-module-chuyên-gia-tiếng-anh--accent-module-2)
   - [C. Module Dịch Thuật Học Thuật EnViT5](#c-module-dịch-thuật-học-thuật-envit5-module-3)
5. [Khởi Chạy Ứng Dụng & Đo Benchmark So Sánh](#5-khởi-chạy-ứng-dụng--đo-benchmark-so-sánh)
6. [Cách Tùy Chỉnh Tham Số (Hyperparameters) Cho GPU](#6-cách-tùy-chỉnh-tham-số-hyperparameters-cho-gpu)
7. [Xử Lý Các Lỗi Thường Gặp (Troubleshooting)](#7-xử-lý-các-lỗi-thường-gặp-troubleshooting)

---

## 1. TỔNG QUAN KIẾN TRÚC HỆ THỐNG

Hệ thống được thiết kế theo mô hình **Phân rã 2 Chuyên Gia Độc Lập (Dual-Specialist Architecture)** thay thế cho việc ép một mô hình duy nhất gánh toàn bộ ngôn ngữ:

```
                  ┌───────────────────────────────┐
                  │      01_AUDIO_ROUTER          │
                  │ (Định tuyến Ngôn ngữ & Accent)│
                  └──────────────┬────────────────┘
                                 │
                 ┌───────────────┴───────────────┐
                 ▼                               ▼
    ┌───────────────────────────┐   ┌───────────────────────────┐
    │ 02_MODULE_VI_SPECIALIST   │   │ 03_MODULE_EN_SPECIALIST   │
    │ - Whisper LoRA Tiếng Việt │   │ - Whisper LoRA Tiếng Anh  │
    │ - Bảo toàn 5 dấu thanh    │   │ - Bắt chuẩn Accent VN     │
    │ - Giữ thuật ngữ CNTT      │   │ - Thuật ngữ công nghệ     │
    └─────────────┬─────────────┘   └─────────────┬─────────────┘
                  │                               │
                  └───────────────┬───────────────┘
                                  ▼
                    ┌───────────────────────────┐
                    │   04_TRANSLATION_MODULE   │
                    │ (EnViT5 Dịch Thuật 2 Chiều│
                    │       VI <-> EN)          │
                    └───────────────────────────┘
```

---

## 2. CẤU TRÚC THƯ MỤC & CÁCH LƯU DỮ LIỆU

### 📂 Vị trí lưu trữ dữ liệu âm thanh gốc:
1. **Âm thanh Tiếng Việt:**
   - Thư mục: `d:/TailieuNPKH/classbridge/backend/data/samples/samples_vi/`
   - Tên file chuẩn: `vimd_<vùng>_<tỉnh>_<spk>_<stt>.wav` (Đi kèm file `.txt` cùng tên chứa nội dung lời thoại).
2. **Âm thanh Tiếng Anh & Accent:**
   - Thư mục: `d:/TailieuNPKH/classbridge/backend/data/samples/`
   - Tên file chuẩn: `en_accent_<tên_accent>_<spk>_<stt>.wav` (Đi kèm file `.txt` chứa transcript).
   - Dữ liệu bổ trợ giọng Việt: `d:/TailieuNPKH/classbridge/training/data/viet_english_accent/audio/`

### 📄 Cấu trúc 1 dòng trong file Manifest (`.jsonl`):
Mỗi dòng là một chuỗi JSON hợp lệ với các trường chuẩn:
```json
{
  "audio": "d:/TailieuNPKH/classbridge/backend/data/samples/en_accent_India_01_00954.wav",
  "audio_filepath": "d:/TailieuNPKH/classbridge/backend/data/samples/en_accent_India_01_00954.wav",
  "text": "She wrote it, you bozos.",
  "language": "en",
  "speaker_id": "spk_en_01",
  "accent": "India_and_South_Asia"
}
```

---

## 3. CÁCH CHỈNH SỬA / THÊM MỚI DỮ LIỆU HUẤN LUYỆN

Khi bạn muốn **thay đổi dữ liệu**, **bổ sung thêm giọng đọc mới** hoặc **đổi tập mẫu**:

### Bước 1: Thêm file âm thanh vào thư mục
- Copy các file `.wav` mới vào thư mục tương ứng (`samples_vi` hoặc `samples`).
- Tạo file `.txt` cùng tên chứa nội dung phiên âm chính xác.
- *Lưu ý về file âm thanh:* Chuẩn format là WAV, 16kHz, Mono, thời lượng từ 1 đến 30 giây.

### Bước 2: Chạy lại script làm sạch và tạo Manifest tự động
- **Đối với Tiếng Việt:**
  ```powershell
  & "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\01_chuan_bi_du_lieu_vi.py
  ```
- **Đối với Tiếng Anh:**
  ```powershell
  & "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\01_chuan_bi_du_lieu_en.py
  ```
Script sẽ tự động:
- Quét kiểm tra tính toàn vẹn từng file bằng thư viện `soundfile` (loại trừ ngay file hỏng/file 0 byte).
- Tự động chia tỉ lệ: **90% tập Train** và **10% tập Validation**.

---

## 4. QUY TRÌNH 4 BƯỚC HUẤN LUYỆN TỪ A ĐẾN Z

### A. MODULE CHUYÊN GIA TIẾNG VIỆT (MODULE 1)
```powershell
# Bước 1: Chuẩn bị và phân chia tập dữ liệu
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\01_chuan_bi_du_lieu_vi.py

# Bước 2: Huấn luyện LoRA (Mặc định 1 epoch, tối ưu GPU RTX 3050)
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\02_train_whisper_vi_lora.py --epochs 1

# Bước 3: Merge LoRA và xuất sang CTranslate2 Float16
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\03_xuat_model_vi_ct2.py

# Bước 4: Kiểm tra độ chính xác và độ trễ trên GPU
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\kiem_tra_chuan_am_tieng_viet.py
```

### B. MODULE CHUYÊN GIA TIẾNG ANH & ACCENT (MODULE 2)
```powershell
# Bước 1: Chuẩn bị và phân chia dữ liệu tiếng Anh
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\01_chuan_bi_du_lieu_en.py

# Bước 2: Huấn luyện LoRA Tiếng Anh & Accent
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\02_train_whisper_en_accent_lora.py --epochs 1

# Bước 3: Merge LoRA và xuất sang CTranslate2 Float16
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\03_xuat_model_en_ct2.py

# Bước 4: Kiểm tra độ chính xác và độ trễ trên GPU
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\kiem_tra_chuan_am_tieng_anh.py
```

### C. MODULE DỊCH THUẬT HỌC THUẬT ENVIT5 (MODULE 3)
```powershell
# Bước 1: Huấn luyện LoRA EnViT5 song ngữ
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\03_TRAIN_DICH_THUAT\01_train_envit5_academic.py

# Bước 2: Kiểm tra điểm số BLEU và độ trễ dịch thuật trên GPU
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\03_TRAIN_DICH_THUAT\kiem_tra_dich_thuat_bleu.py
```

---

## 5. KHỞI CHẠY ỨNG DỤNG & ĐO BENCHMARK SO SÁNH

### 🕹️ Cách 1: Sử dụng Master Script 1-Click (Khuyên Dùng)
Chạy toàn bộ ứng dụng (AI Service GPU + Web Frontend):
```powershell
powershell -ExecutionPolicy Bypass -File .\classbridge\start-classbridge.ps1 -Mode run
```

### 🚀 Cách 2: Chạy trực tiếp AI Backend Service (Port 8000)
```powershell
cd d:\TailieuNPKH\classbridge\backend\ai-service
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 🚀 Cách 3: Kiểm Tra Trực Tiếp Model Hiện Tại (1 Luồng ASR ➜ Dịch thuật)
Chạy script kiểm tra trực tiếp 1 luồng:
```powershell
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\06_danh_gia_so_sanh_wer_bleu.py
```

---

## 6. CÁCH TÙY CHỈNH THAM SỐ (HYPERPARAMETERS) CHO GPU

Tất cả các script huấn luyện (`02_train_...`) đều hỗ trợ tham số dòng lệnh:

| Tham số | Ý nghĩa | Giá trị khuyến nghị (RTX 3050 4GB) | Giải thích |
| :--- | :--- | :--- | :--- |
| `--epochs` | Số vòng lặp huấn luyện | `1` đến `3` | 1 epoch mất khoảng 35 - 60 giây |
| `--batch_size` | Số mẫu mỗi batch | `4` | Vừa vặn 4GB VRAM, không bị tràn bộ nhớ (OOM) |
| `--lr` | Tốc độ học (Learning rate) | `1e-4` (0.0001) | Tối ưu cho LoRA Adapter |
| `--smoke_test` | Chế độ chạy thử nhanh | Thêm cờ `--smoke_test` | Chỉ chạy 50 steps để kiểm tra code |

**Ví dụ chạy train 3 epoch với batch size 4:**
```powershell
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\02_train_whisper_en_accent_lora.py --epochs 3 --batch_size 4
```

---

## 7. XỬ LÝ CÁC LỖI THƯỜNG GẶP (TROUBLESHOOTING)

### 1. Lỗi `System error: Error opening '...wav'`
- **Nguyên nhân:** File âm thanh bị xóa dở dang, đường dẫn sai hoặc file rỗng 0 bytes.
- **Khắc phục:** Chạy lại file `01_chuan_bi_du_lieu_...py`. Script hiện tại đã tích hợp sẵn lệnh `soundfile.info()` để tự động loại bỏ mọi file lỗi trước khi đưa vào train.

### 2. Lỗi `CUDA Out of Memory (OOM)`
- **Nguyên nhân:** GPU RTX 3050 có 4GB VRAM bị các tiến trình khác (Chrome, game, app khác) chiếm dụng.
- **Khắc phục:**
  - Giữ nguyên `--batch_size 4` (hoặc giảm xuống `2`).
  - Đóng bớt các ứng dụng chiếm GPU trước khi bấm train.

### 3. Mô hình nạp sai đường dẫn
- **Cơ chế nạp tự động:** Cả `vi_speech_recognizer.py` và `en_speech_recognizer.py` đều ưu tiên nạp mô hình cục bộ vừa train (`model_vi_ct2` và `model_en_ct2`). Nếu chưa tìm thấy, hệ thống sẽ tự động chuyển sang mô hình dự phòng (fallback) mà không làm ngắt quãng chương trình.

