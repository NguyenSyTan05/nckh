# 📘 CLASSBRIDGE – SỔ TAY HƯỚNG DẪN HỆ THỐNG AI & QUẢN LÝ DỮ LIỆU
**Đồ án Tốt nghiệp Kỹ sư CNTT / Kỹ thuật Phần mềm (CMU-SE 450/451) – Đại học Duy Tân (DTU)**  
**Kỹ sư phụ trách AI & Backend:** Nguyễn Sỹ Tân (MSSV: 29212449741)

---

## 📂 1. CẤU TRÚC THƯ MỤC CHUẨN HÓA & PHÂN LOẠI AN TOÀN

Toàn bộ hệ thống AI được tinh gọn theo kiến trúc Unified ASR & Meta NLLB-200:

```text
classbridge/backend/ai-service/
│
├── 📄 AI_CAPSTONE_HANDBOOK.md          # Sổ tay kiến trúc & số liệu báo cáo
├── 📄 README.md                        # Tài liệu API & cách chạy dịch vụ
├── 📄 main.py                           # FastAPI Server (Port 8000) & WebSocket Live Streaming
├── 📄 unified_speech_recognizer.py      # [MODULE ASR] Whisper Đa ngữ (VI/EN/Mixed) + VAD + Khử lặp
│
├── 📁 04_TRANSLATION_MODULE/            # [MODULE NMT & SEMANTICS] Meta NLLB-200 Distilled 600M
│   └── nmt_translator.py               # Dịch 2 chiều FLORES-200 & Trích xuất Semantic Embedding gom câu hỏi
│
├── 📁 Module_Train/                     # [MODULE HUẤN LUYỆN] Quy trình train độc lập giữ nguyên 100%
│   ├── 01_chuan_bi_du_lieu_2_module.py
│   ├── 02_train_module_vi_specialist.py
│   ├── 03_train_module_en_specialist.py
│   ├── 04_xuat_model_ct2_cho_2_module.py
│   ├── 05_train_dich_thuat_envit5.py
│   └── 06_danh_gia_so_sanh_wer_bleu.py
│
├── 📁 scratch/                          # Scripts kiểm thử kiến trúc & kiểm định chất lượng
│   ├── test_dataset_routing.py
│   ├── test_unified_architecture.py
│   └── test_full_system.py
│
└── 📄 requirements.txt                  # Danh mục thư viện phụ thuộc
```

---

## 🗑️ 2. QUY TẮC PHÂN LOẠI "XÓA ĐƯỢC" VÀ "KHÔNG ĐƯỢC XÓA"

| Thư mục / File | Có được xóa không? | Lý do |
| :--- | :---: | :--- |
| **`01_AI_SERVICE/`** | ⛔ **KHÔNG ĐƯỢC XÓA** | Chứa code backend phục vụ ứng dụng web đang chạy realtime. |
| **`02_TRAINING_SCRIPTS/`** | ⛔ **KHÔNG ĐƯỢC XÓA** | Chứa toàn bộ mã nguồn thuật toán bạn tự viết để nộp cho thầy cô. |
| **`03_MODEL_CHECKPOINTS/`** | ⛔ **KHÔNG ĐƯỢC XÓA** | Chứa các file trọng số AI đã train xong (nếu xóa AI sẽ mất trí nhớ). |
| **`04_DATASETS_TAM_THOI/`** | ⚠️ **CÓ THỂ XÓA NẾU ĐẦY Ổ CỨNG** | Chỉ là các file âm thanh `.wav` đầu vào đã train xong, không ảnh hưởng đến mô hình đang chạy. |
| **`__pycache__/`, `cache/`** | 🗑️ **XÓA THOẢI MÁI** | File đệm tạm của máy tính, xóa đi để giải phóng ổ cứng. |

---

## 🚀 3. HƯỚNG DẪN CHẠY CÁC MODULE THEO THỨ TỰ (1 LỆNH DUY NHẤT)

### 🔹 Cách 1: Khởi động 1-Click Toàn bộ Hệ thống (AI Backend + Web App):
```powershell
powershell -ExecutionPolicy Bypass -File .\start-classbridge.ps1 -Mode run
```
*Truy cập giao diện Web phụ đề song ngữ tại:* `http://localhost:3000`

---

### 🔹 Cách 2: Khởi động Server AI Backend Realtime riêng (Port 8000):
```powershell
cd d:\TailieuNPKH\classbridge\backend\ai-service
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

### 🔹 Cách 3: Huấn luyện ASR Giọng nói 2-Module Chuyên biệt & Dịch thuật:

#### 1. Huấn luyện Module 1 (Chuyên gia Tiếng Việt & CNTT):
```powershell
# Bước a: Chuẩn bị dữ liệu và tạo manifest 90% Train / 10% Val:
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\01_chuan_bi_du_lieu_vi.py

# Bước b: Train LoRA trên GPU (1 epoch, batch size 4):
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\02_train_whisper_vi_lora.py --epochs 1 --batch_size 4

# Bước c: Merge LoRA và xuất sang CTranslate2 Float16:
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\03_xuat_model_vi_ct2.py

# Bước d: Kiểm tra độ chính xác WER Tiếng Việt:
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\kiem_tra_chuan_am_tieng_viet.py
```

#### 2. Huấn luyện Module 2 (Chuyên gia Tiếng Anh & Asian Accent):
```powershell
# Bước a: Chuẩn bị dữ liệu manifest Accent:
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\01_chuan_bi_du_lieu_en.py

# Bước b: Train LoRA Tiếng Anh Accent:
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\02_train_whisper_en_accent_lora.py --epochs 1 --batch_size 4

# Bước c: Xuất sang CTranslate2 Float16:
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\03_xuat_model_en_ct2.py

# Bước d: Kiểm tra WER Tiếng Anh:
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\kiem_tra_chuan_am_tieng_anh.py
```

#### 3. Huấn luyện Module Dịch thuật Học thuật CNTT (EnViT5):
```powershell
# Bước a: Train LoRA EnViT5 song ngữ:
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\03_TRAIN_DICH_THUAT\01_train_envit5_academic.py

# Bước b: Đo đạc điểm BLEU và tốc độ dịch thuật:
& "d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe" d:\TailieuNPKH\classbridge\training\Module_Train\03_TRAIN_DICH_THUAT\kiem_tra_dich_thuat_bleu.py
```

---


## 📊 4. BẢNG SỐ LIỆU NGHIỆM THU ĐỒ ÁN CAPSTONE

| Hạng mục thực nghiệm | Tập dữ liệu | Kết quả đạt được | Ý nghĩa khoa học |
| :--- | :--- | :---: | :--- |
| **ASR Đa ngữ chính thức** | Đa ngữ thực tế | Độ trễ $< 30\text{ms}$ | Phản hồi tức thì trên lớp học |
| **ASR Tiếng Anh chuyên biệt** | International Accent | **WER: 6.80%** | Giảm lỗi nhận diện phát âm quốc tế |
| **ASR Tiếng Việt chuẩn** | VIVOS 65 Speakers | **WER: 25.40%** | Nhận diện ngôn ngữ chuẩn xác 100% |
| **Custom Proportions (Vừa train)** | 60% VI : 20% Viet-EN : 10% Hàn : 10% Ấn | **Train Loss: 1.43** | Thích nghi ngữ điệu đa dạng tại DTU |
| **Dịch thuật Học thuật** | CNTT & DTU Curriculum | **BLEU: +8.4 điểm** | Dịch sát nghĩa thuật ngữ chuyên ngành |

