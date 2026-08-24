# 04. Quy Trình Huấn Luyện & Tối Ưu AI (AI Training & Fine-Tuning Guide)

---

## 1. Mục Tiêu Nghiên Cứu & Thách Thức

Trong môi trường giảng đường đại học (đặc biệt các môn CNTT & Khoa học kỹ thuật), các mô hình ASR và NMT phổ quát gặp các hạn chế:
1. Nhận diện kém tên biến, cú pháp lệnh và thuật ngữ kỹ thuật tiếng Anh khi được đọc bởi người Việt.
2. Phương ngữ 3 miền (Bắc, Trung, Nam) có ngữ điệu và phát âm khác biệt lớn.
3. Hiện tượng nói xen kẽ song ngữ (*Code-switching*) khiến mô hình ASR dễ chuyển sai mã ngôn ngữ (Language flipping).
4. Hiện tượng *Catastrophic Forgetting* khi fine-tune mô hình đa ngữ (làm tốt tiếng này nhưng mất khả năng nhận diện tiếng khác).

---

## 2. Chuẩn Bị & Quản Lý Tập Dữ Liệu (Dataset Manifest)

### 2.1. Định Dạng File Manifest (`JSONL`)
Dữ liệu huấn luyện được cấu trúc dưới dạng các file `.jsonl` trong thư mục `classbridge/training/data/`:

```json
{"audio": "data/samples/sample_en_01.wav", "text": "Welcome to today's lecture on artificial intelligence and machine learning.", "language": "en", "speaker_id": "lecturer_01", "accent": "en_us"}
{"audio": "data/samples/sample_vi_01.wav", "text": "Kiểm thử phần mềm giúp nâng cao chất lượng phần mềm và độ tin cậy của hệ thống.", "language": "vi", "speaker_id": "lecturer_02", "accent": "vi_hn"}
{"audio": "data/samples/sample_mixed_01.wav", "text": "Hôm nay chúng ta sẽ tìm hiểu về mô hình Deep Learning và Neural Network.", "language": "vi", "speaker_id": "lecturer_02", "accent": "vi_mixed"}
```

### 2.2. Các Nguồn Dữ Liệu Tích Hợp
- **Tập VIVOS**: Bộ ngữ liệu tiếng Việt giọng đọc chuẩn phục vụ huấn luyện nền tảng.
- **Tập ViMD (Vietnamese Multi-Dialect)**: Dữ liệu giọng nói đa vùng miền 63 tỉnh thành Việt Nam.
- **DTU Academic Vocabulary**: Ngữ liệu bài giảng và từ vựng CNTT được thu thập và tổng hợp tại trường.
- **Personalized Voice Capture**: Thu âm trực tiếp 10-15 câu mẫu từ giảng viên để cá nhân hóa trọng số LoRA.

---

## 3. Chiến Lược Fine-Tuning LoRA Decoder-Only

Để giải quyết bài toán chống quên ngôn ngữ và giảm tải tài nguyên tính toán (chỉ cần GPU 4GB VRAM):
- **Cố định (Freeze) toàn bộ Encoder** và module nhận diện ngôn ngữ.
- **Chỉ gắn LoRA Adapters** vào các ma trận chiếu `q_proj` và `v_proj` của **Decoder**.
- **Cấu hình Hyperparameters tiêu chuẩn**:
  - `lora_r = 16` hoặc `32`
  - `lora_alpha = 32` hoặc `64`
  - `lora_dropout = 0.05`
  - `learning_rate = 1e-4` (giảm dần qua các micro-stages)
  - `batch_size = 1`, `gradient_accumulation_steps = 8`

---

## 4. Báo Cáo Kết Quả Thực Nghiệm (Empirical Evaluation Report)

Dưới đây là kết quả kiểm thử trên tập đánh giá ASR song ngữ (Môi trường RTX 3050 4GB VRAM):

| Checkpoint / Giai Đoạn | EN Samples | VI Samples | EN WER (%) ↓ | VI WER (%) ↓ | EN/VI Lang Acc (%) ↑ | Đánh Giá Triển Khai |
|---|---:|---:|---:|---:|---:|---|
| **Baseline (Mô hình gốc)** | — | — | 12.62% | 41.99% | 100% / 100% | Nhận dạng tiếng Việt kém |
| **Full Fine-tune (Giai đoạn 3)** | 2.112 | 2.112 | 5.34% | 92.14% | 100% / 5% | ❌ Bị Catastrophic Forgetting |
| **`decoder-micro1` (Đề xuất)** | 32 | 32 | **7.28%** | **25.40%** | **100% / 100%** | ✅ **Chọn làm mô hình chính (VI & LangID)** |
| **`decoder-micro4` (Đề xuất)** | 32 | 32 | **6.80%** | 25.84% | 100% / 100% | ✅ **Chọn làm Specialist tiếng Anh** |

> **Kết luận thực nghiệm**:
> - Mô hình `decoder-micro1` giảm WER tiếng Việt từ **41.99% xuống 25.40%** mà vẫn duy trì độ chính xác nhận diện ngôn ngữ 100%.
> - Mô hình `decoder-micro4` đạt độ chính xác cao nhất cho tiếng Anh chuyên ngành (**WER 6.80%**).
> - Hệ thống kết hợp phân luồng: `micro1` xác định ngôn ngữ & dịch tiếng Việt, sau đó kích hoạt `micro4` cho các câu tiếng Anh.

---

## 5. Quy Trình Xuất Mô Hình Tối Ưu CTranslate2 (Export INT8)

Sau khi huấn luyện xong trọng số LoRA:
1. **Hợp nhất trọng số (Merge LoRA)**: Tích hợp adapter LoRA vào mô hình gốc Whisper.
2. **Chuyển đổi sang CTranslate2**:
```powershell
python training/export_whisper_lora.py \
  --model_dir classbridge/training/outputs/whisper-merged \
  --output_dir classbridge/backend/ai-service/whisper-multi-accent-ct2 \
  --quantization int8_float16
```
3. Khởi động lại dịch vụ AI, hệ thống sẽ tự động phát hiện và nạp mô hình CT2 mới tại `whisper-multi-accent-ct2`.
