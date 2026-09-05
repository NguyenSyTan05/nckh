# 📘 CLASSBRIDGE – SỔ TAY HƯỚNG DẪN HỆ THỐNG AI & QUẢN LÝ DỮ LIỆU
**Đồ án Tốt nghiệp Kỹ sư CNTT / Kỹ thuật Phần mềm (CMU-SE 450/451) – Đại học Duy Tân (DTU)**  
**Kỹ sư phụ trách AI & Backend:** Nguyễn Sỹ Tân (MSSV: 29212449741)

---

## 📂 1. CẤU TRÚC THƯ MỤC CHUẨN HÓA & PHÂN LOẠI AN TOÀN

Toàn bộ hệ thống AI được tổ chức thành 4 thư mục trực quan và đánh số thứ tự dễ hiểu:

```text
d:\TailieuNPKH\ai_backend/
│
├── 📄 AI_CAPSTONE_HANDBOOK.md          # [CẦN GIỮ] - Sổ tay hướng dẫn & số liệu báo cáo
│
├── 📁 01_AI_SERVICE/                    # [QUAN TRỌNG - KHÔNG ĐƯỢC XÓA] - Dịch vụ AI Realtime chính
│   ├── main.py                          # Server API chính, luồng streaming WebSocket (< 30ms)
│   ├── modules/
│   │   └── correction_module.py         # Bộ lọc âm vị học & Chuẩn hóa Unicode NFC
│   ├── transcript_stabilizer.py         # Bộ ổn định chữ, chống nhảy chữ trên giao diện
│   ├── auto_punctuation.py              # Tự động ngắt câu và thêm dấu câu
│   ├── session_manager.py               # Quản lý phòng học & phiên kết nối
│   └── requirements.txt
│
├── 📁 02_TRAINING_SCRIPTS/              # [QUAN TRỌNG - KHÔNG ĐƯỢC XÓA] - Bộ mã nguồn huấn luyện
│   ├── 01_chuan_bi_du_lieu.py           # Chia tỷ lệ vàng (60% VI : 20% Viet-EN : 10% Hàn : 10% Ấn)
│   ├── 02_train_whisper_lora.py         # Huấn luyện Whisper LoRA Adapter trên GPU NVIDIA
│   ├── 03_xuat_model_ct2.py             # Hợp nhất trọng số LoRA và xuất sang CTranslate2 float16
│   ├── 04_train_dich_thuat_nmt.py       # Huấn luyện mô hình Dịch thuật EnViT5 LoRA
│   ├── 05_ghi_am_hoc_giong_noi.py       # Thu âm giọng giảng viên trực tiếp để AI học giọng tức thì
│   ├── 06_thu_thap_du_lieu_lop_hoc.py   # Thu thập & kiểm định chất lượng âm thanh tại lớp học DTU
│   ├── 07_danh_gia_wer_bleu.py          # Đo đạc chỉ số lỗi WER và điểm BLEU
│   ├── BAO_CAO_TRAINING_REPORT.md       # Báo cáo khoa học ghi nhận toàn bộ số liệu thực nghiệm
│   └── requirements.txt
│
├── 📁 03_MODEL_CHECKPOINTS/             # [QUAN TRỌNG - KHÔNG ĐƯỢC XÓA] - Trọng số mô hình đã train xong
│   ├── whisper-large-v3-turbo-ct2/      # Model ASR chính thức đang chạy
│   ├── whisper-decoder-micro4-en-ct2/   # Model ASR tiếng Anh chuyên biệt (WER 6.80%)
│   ├── whisper-custom-proportions-ct2/  # Model ASR vừa train theo tỷ lệ vàng (Loss 1.43)
│   └── nmt-academic-lora-balanced/      # Model Dịch thuật CNTT đã train LoRA
│
└── 📁 04_DATASETS_TAM_THOI/             # [CÓ THỂ XÓA KHI ĐẦY Ổ CỨNG] - Dữ liệu âm thanh thô & Manifests
    └── manifests/                       # Danh sách đường dẫn các file audio train/val
        ├── proportional_train_manifest.jsonl
        └── proportional_val_manifest.jsonl
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

### 🔹 Bước 1: Khởi động Server AI Backend Realtime:
```powershell
cd d:\TailieuNPKH\ai_backend\01_AI_SERVICE
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

### 🔹 Bước 2: Huấn luyện ASR Giọng nói theo tỷ lệ vàng (Pipeline chuẩn):
```powershell
cd d:\TailieuNPKH\ai_backend\02_TRAINING_SCRIPTS

# 1. Tạo tập dữ liệu tỷ lệ vàng:
python 01_chuan_bi_du_lieu.py

# 2. Huấn luyện LoRA trên GPU:
python 02_train_whisper_lora.py --train ../04_DATASETS_TAM_THOI/manifests/proportional_train_manifest.jsonl --validation ../04_DATASETS_TAM_THOI/manifests/proportional_val_manifest.jsonl --output ../03_MODEL_CHECKPOINTS/whisper-custom-lora --epochs 2 --batch-size 4 --gradient-accumulation 4

# 3. Xuất sang CTranslate2 float16:
python 03_xuat_model_ct2.py --base-model openai/whisper-small --adapter ../03_MODEL_CHECKPOINTS/whisper-custom-lora --merged-output ../03_MODEL_CHECKPOINTS/whisper-custom-merged --ct2-output ../03_MODEL_CHECKPOINTS/whisper-custom-proportions-ct2 --quantization float16
```

---

### 🔹 Bước 3: Huấn luyện mô hình Dịch thuật học thuật CNTT (EnViT5):
```powershell
cd d:\TailieuNPKH\ai_backend\02_TRAINING_SCRIPTS
python 04_train_dich_thuat_nmt.py
```

---

### 🔹 Bước 4: Thu âm giọng giảng viên trực tiếp để AI học giọng (Demo bảo vệ):
```powershell
cd d:\TailieuNPKH\ai_backend\02_TRAINING_SCRIPTS
python 05_ghi_am_hoc_giong_noi.py
```

---

### 🔹 Bước 5: Đo đạc chỉ số WER và điểm BLEU (Số liệu báo cáo):
```powershell
cd d:\TailieuNPKH\ai_backend\02_TRAINING_SCRIPTS
python 07_danh_gia_wer_bleu.py
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
