# THƯ MỤC: classbridge/training/
## Phân Hệ Huấn Luyện Mô Hình & Đánh Giá Độ Chính Xác (ASR & NMT)

**Tác giả:** Nguyễn Sỹ Tân  
**Mục đích:** Cung cấp toàn bộ công cụ huấn luyện mô hình giọng nói cá nhân, giọng vùng miền (Accent), thuật ngữ CNTT và mô hình dịch thuật EnViT5 LoRA, cùng với công cụ đánh giá chỉ số WER và BLEU.

---

### 1. BẢNG TRA CỨU CHI TIẾT TỪNG TỆP TIN TRONG THƯ MỤC `training/`

| Tên File / Thư mục | Công Dụng Chi Tiết | Có Cần Nữa Không? Để Làm Gì? |
| :--- | :--- | :--- |
| **`train_master_manager.py`** | Menu dòng lệnh tương tác tổng hợp: Quản lý chạy train Module 1, Module 2, Module 3 và đánh giá Benchmark WER/BLEU. | **BẮT BUỘC NẾU MUỐN TRAIN**. Đây là file quản lý tập trung toàn bộ tiến trình huấn luyện. |
| **`finetune_whisper_lora.py`** | Kịch bản cốt lõi thực hiện fine-tune Whisper bằng kỹ thuật LoRA (PEFT) trên GPU CUDA, lưu checkpoint mô hình. | **CẦN THIẾT**: Dùng khi bạn muốn tiếp tục train Whisper với dữ liệu bài giảng mới. |
| **`export_whisper_lora.py`** | Chuyển đổi mô hình PyTorch LoRA sau khi train sang định dạng CTranslate2 (CT2 Float16/INT8) siêu tốc. | **CẦN THIẾT**: Sau khi train xong, bắt buộc chạy file này để xuất sang model CT2 cho `ai-service` chạy real-time. |
| **`train_accent_module.py`** | Kịch bản chuyên huấn luyện nhận dạng tiếng Anh với giọng vùng miền (Vietnamese English Accent) từ tập EDACC. | **CẦN THIẾT**: Dùng để huấn luyện Module 2 (EN Specialist). |
| **`train_translation_module.py`** | Huấn luyện mô hình dịch thuật EnViT5 với dữ liệu cặp câu Anh-Việt chuyên ngành CNTT. | **CẦN THIẾT**: Dùng để huấn luyện Module dịch thuật học thuật. |
| **`train_balanced_translation.py`** | Huấn luyện cân bằng trọng số dịch thuật 2 chiều (En->Vi và Vi->En) tránh lệch ngôn ngữ. | **CẦN THIẾT**: Tạo ra trọng số `nmt-academic-lora-balanced`. |
| **`prepare_dtu_academic_vocab.py`** | Quét tài liệu học thuật DTU, trích xuất danh sách từ vựng chuyên ngành CNTT để chèn vào tokenizer. | **CẦN THIẾT**: Giúp mô hình không bao giờ viết sai các từ chuyên ngành (Docker, Cloud, Microservices...). |
| **`live_stt_demo.py`** | Công cụ demo kiểm tra nhanh ASR trực tiếp từ micro trong terminal mà không cần bật web. | **TIỆN ÍCH HỖ TRỢ**: Rất hữu ích để kiểm tra micro và GPU độc lập. |
| **`record_classbridge_dataset.py`** | Script hỗ trợ người dùng tự ghi âm câu mẫu bằng mic để tạo tập dữ liệu giọng nói riêng. | **TIỆN ÍCH HỖ TRỢ**: Dùng khi bạn muốn cá nhân hóa mô hình cho giọng của riêng mình. |
| **`backend/utils.py`** | Chứa các hàm tiện ích tiền xử lý dữ liệu cho tập ViMD (Vietnam Multi-dialect Dataset). | **TIỆN ÍCH PHỤ**: Dùng cho khâu chuẩn bị dữ liệu ViMD. |
| **`install_ai_deps.ps1`** | Kịch bản PowerShell tự động cài đặt PyTorch CUDA và các thư viện học máy. | **CẦN KHI SETUP**: Dùng khi cài đặt môi trường máy mới. |
| **`requirements.txt`** | Danh sách thư viện Python phục vụ huấn luyện (torch, transformers, datasets, peft...). | **BẮT BUỘC**. |
| **`data/`** | Thư mục chứa các file manifest mẫu dạng JSONL (`audio_path`, `text`, `language`). | **CẦN THIẾT**: Cung cấp đường dẫn dữ liệu đầu vào cho quá trình train. |

---

### 2. CÁC LỆNH CHÍNH ĐỂ HUẤN LUYỆN & ĐÁNH GIÁ:

1. **Mở Menu Huấn Luyện Tổng Hợp**:
   ```powershell
   cd d:\TailieuNPKH\classbridge\training
   ..\backend\ai-service\.venv\Scripts\python.exe train_master_manager.py
   ```

2. **Chạy thử Demo ASR trên Terminal**:
   ```powershell
   ..\backend\ai-service\.venv\Scripts\python.exe live_stt_demo.py --language auto --model base
   ```

3. **Đánh giá chỉ số WER và BLEU**:
   Chọn chức năng `[5]` trong menu `train_master_manager.py`.
