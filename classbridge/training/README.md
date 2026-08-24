# ClassBridge AI Training & Accuracy Optimization Guide
Hướng Dẫn Huấn Luyện Mô Hình AI & Tối Ưu Độ Chính Xác Dịch Thuật Song Ngữ

Hệ thống AI của ClassBridge tự động nhận diện ngôn ngữ (**Tiếng Anh / Tiếng Việt / Song ngữ pha trộn**), ghi lời gốc chuẩn xác theo thời gian thực và dịch sang ngôn ngữ còn lại. 

Tài liệu này hướng dẫn bạn cách sử dụng **AI Training Module** để huấn luyện mô hình giọng nói cá nhân, đa vùng miền, thuật ngữ chuyên ngành (IT/AI) và xuất mô hình sang **CTranslate2 INT8** để đạt tốc độ xử lý siêu tốc (**<50ms**).

---

## 🚀 Các Phương Thức Huấn Luyện AI

### 1. Quản Lý Huấn Luyện Trực Tiếp (Interactive Master Menu)

Chạy trình quản lý tổng thể:
```powershell
python ai-service/train_master_manager.py
```
Menu tương tác cung cấp 5 lựa chọn:
- **[1] Train Giọng Nói Cá Nhân hóa**: Thu âm trực tiếp 10-15 câu mẫu và Fine-Tune Whisper cho giọng của bạn (Độ chính xác >99%).
- **[2] Train Nhận Dạng Đa Giọng Nói**: Huấn luyện giọng Tiếng Anh quốc tế (Ấn Độ, Châu Á, Anh, Mỹ) và Tiếng Việt 3 miền (Bắc, Trung, Nam).
- **[3] Train Dịch Thuật Học Thuật 2 Chiều**: Fine-Tune mô hình NMT (EnViT5 / MarianMT) với từ điển thuật ngữ IT/AI chuyên ngành.
- **[4] Đánh Giá Chỉ Số Độ Chính Xác**: Đánh giá WER (Word Error Rate) và BLEU score.
- **[5] Chạy AI Training Pipeline Toàn Diện**: Chạy quy trình end-to-end tự động từ nạp dữ liệu, train LoRA đến xuất mô hình CTranslate2.

---

### 2. Chạy Pipeline Huấn Luyện Tự Động (Unified Pipeline CLI)

Chạy pipeline toàn diện bằng lệnh duy nhất:
```powershell
python training/train_ai_pipeline.py --mode all --manifest data/bilingual_sample_manifest.jsonl
```

#### Các Chế Độ Chạy Chi Tiết (`--mode`):
- `--mode prep`: Kiểm tra và xác thực định dạng dữ liệu trong file manifest JSONL.
- `--mode asr`: Fine-tune mô hình Whisper LoRA cho nhận dạng giọng nói.
- `--mode nmt`: Fine-tune mô hình NMT LoRA cho dịch thuật song ngữ 2 chiều.
- `--mode export`: Chuyển đổi và nén mô hình sang CTranslate2 INT8 format cho real-time.
- `--mode eval`: Tính toán và hiển thị chỉ số WER (Word Error Rate) và BLEU score.

---

## 📊 Định Dạng Dữ Liệu Huấn Luyện (Dataset Manifest)

File dữ liệu huấn luyện có định dạng JSONL (`data/bilingual_sample_manifest.jsonl`):

```json
{"audio": "data/samples/sample_en_01.wav", "text": "Welcome to today's lecture on artificial intelligence and machine learning.", "language": "en", "speaker_id": "lecturer_01", "accent": "en_us"}
{"audio": "data/samples/sample_vi_01.wav", "text": "Kiểm thử phần mềm giúp nâng cao chất lượng phần mềm và độ tin cậy của hệ thống.", "language": "vi", "speaker_id": "lecturer_02", "accent": "vi_hn"}
{"audio": "data/samples/sample_mixed_01.wav", "text": "Hôm nay chúng ta sẽ tìm hiểu về mô hình Deep Learning và Neural Network.", "language": "vi", "speaker_id": "lecturer_02", "accent": "vi_mixed"}
```

---

## ⚡ Nạp Mô Hình Đã Train Vào AI Service

Mô hình sau khi train sẽ được tự động lưu vào các thư mục:
- `ai-service/whisper-multi-accent-ct2`: Mô hình CTranslate2 INT8/FP16 siêu tốc cho đa phương ngữ.
- `ai-service/whisper-voice-fine-tuned`: Mô hình LoRA giọng nói cá nhân.
- `ai-service/nmt-academic-lora-balanced`: Mô hình dịch thuật song ngữ cân bằng LoRA mới nhất.
- `ai-service/nmt-academic-lora`: Mô hình dịch thuật học thuật tiêu chuẩn.

Khi bạn khởi động lại ClassBridge AI Service (`npm run dev` hoặc `python ai-service/main.py`), hệ thống sẽ **tự động ưu tiên nạp mô hình đã train** mà không cần cấu hình thêm!

