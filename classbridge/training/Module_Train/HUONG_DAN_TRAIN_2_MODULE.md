# 🎓 HỆ THỐNG HUẤN LUYỆN ĐÃ PHÂN CHIA RÕ RÀNG TIẾNG VIỆT & TIẾNG ANH
**Dự án Capstone & Nghiên cứu Khoa học (NCKH)**  
**Tác giả:** Nguyễn Sỹ Tân (MSSV: 29212449741)  

---

## 🏛️ 1. CẤU TRÚC PHÂN CHIA THƯ MỤC HUẤN LUYỆN

```
d:\TailieuNPKH\classbridge\training\Module_Train/
│
├── 📁 01_TRAIN_TIENG_VIET/              # 🇻🇳 Huấn luyện Chuyên gia Tiếng Việt
│   ├── 01_chuan_bi_du_lieu_vi.py       # [Bước 1] Chuẩn bị dữ liệu VIVOS + Đại học
│   ├── 02_train_whisper_vi_lora.py     # [Bước 2] Train LoRA bảo toàn 5 dấu thanh điệu
│   └── 03_xuat_model_vi_ct2.py         # [Bước 3] Xuất model CTranslate2 Float16 cho GPU
│
├── 📁 02_TRAIN_TIENG_ANH/               # 🇬🇧 Huấn luyện Chuyên gia Tiếng Anh & Accent
│   ├── 01_chuan_bi_du_lieu_en.py       # [Bước 1] Chuẩn bị dữ liệu Viet-English Accent
│   ├── 02_train_whisper_en_accent_lora.py # [Bước 2] Train LoRA nhận diện Accent & CNTT
│   └── 03_xuat_model_en_ct2.py         # [Bước 3] Xuất model CTranslate2 Float16 cho GPU
│
├── 📁 03_TRAIN_DICH_THUAT/              # 🌐 Huấn luyện Dịch thuật Song ngữ EnViT5
│   └── 01_train_envit5_academic.py     # [Bước 1] Train Dịch thuật 2 chiều VI <-> EN
│
└── 📄 06_danh_gia_so_sanh_wer_bleu.py   # 🚀 Kiểm tra 1 luồng Model thống nhất hiện tại (ASR + NMT)
```

---

## 🚀 2. LỆNH CHẠY HUẤN LUYỆN TỪNG PHẦN (POWERSHELL)

### 🇻🇳 1. Chạy Huấn luyện Module Tiếng Việt:
```powershell
# Bước 1: Chuẩn bị dữ liệu
powershell -ExecutionPolicy Bypass -Command "& d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\01_chuan_bi_du_lieu_vi.py"

# Bước 2: Huấn luyện LoRA Tiếng Việt
powershell -ExecutionPolicy Bypass -Command "& d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\02_train_whisper_vi_lora.py --epochs 3"

# Bước 3: Xuất CTranslate2
powershell -ExecutionPolicy Bypass -Command "& d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe d:\TailieuNPKH\classbridge\training\Module_Train\01_TRAIN_TIENG_VIET\03_xuat_model_vi_ct2.py"
```

### 🇬🇧 2. Chạy Huấn luyện Module Tiếng Anh:
```powershell
# Bước 1: Chuẩn bị dữ liệu
powershell -ExecutionPolicy Bypass -Command "& d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\01_chuan_bi_du_lieu_en.py"

# Bước 2: Huấn luyện LoRA Tiếng Anh & Accent
powershell -ExecutionPolicy Bypass -Command "& d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\02_train_whisper_en_accent_lora.py --epochs 3"

# Bước 3: Xuất CTranslate2
powershell -ExecutionPolicy Bypass -Command "& d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe d:\TailieuNPKH\classbridge\training\Module_Train\02_TRAIN_TIENG_ANH\03_xuat_model_en_ct2.py"
```

### 🌐 3. Chạy Huấn luyện Dịch thuật EnViT5:
```powershell
powershell -ExecutionPolicy Bypass -Command "& d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe d:\TailieuNPKH\classbridge\training\Module_Train\03_TRAIN_DICH_THUAT\01_train_envit5_academic.py"
```

### 🚀 4. Kiểm tra Model Thống nhất Hiện tại (1 Luồng ASR ➜ Dịch):
```powershell
powershell -ExecutionPolicy Bypass -Command "& d:\TailieuNPKH\classbridge\backend\ai-service\.venv\Scripts\python.exe d:\TailieuNPKH\classbridge\training\Module_Train\06_danh_gia_so_sanh_wer_bleu.py"
```

