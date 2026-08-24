# Báo cáo huấn luyện ASR Anh–Việt

Ngày chạy: 2026-08-13

## Thiết bị

- NVIDIA GeForce RTX 3050 Laptop GPU, 4 GB VRAM.
- PyTorch 2.11.0 + CUDA 12.8.
- Whisper-small LoRA, batch 1, gradient accumulation 8.

## Quy tắc dữ liệu

- Không sử dụng dữ liệu trong `classbridge/test` để train.
- Validation tách người nói hoàn toàn khỏi train.
- Mỗi giọng tối đa 20 mẫu train và 2 mẫu validation.
- Tập được mở rộng dần, không lấy hết dữ liệu của một giọng.

## Các giai đoạn

| Giai đoạn | Dữ liệu | Kết quả chính |
|---|---:|---|
| 1 | 474 mẫu | EN WER 3,90%; VI WER chưa đạt |
| 2 | 1.224 mẫu | Loss 1,65; CT2 EN WER 4,85%; VI WER 50,44%; VI language accuracy 60% |
| 3 | 4.224 mẫu | Loss 1,46; CT2 EN WER 5,34%; VI WER 92,14%; VI language accuracy 5% |
| Model hiện hành | baseline sản xuất | EN WER 12,62%; VI WER 41,99%; language accuracy EN/VI 100% |

## Quyết định

Không triển khai checkpoint giai đoạn 2 hoặc 3 vì đều kém model hiện hành ở
nhận dạng tiếng Việt và phát hiện ngôn ngữ. Model sản xuất được giữ nguyên.

Hướng train tiếp theo nên khóa encoder/language detector và chỉ gắn LoRA vào
decoder, hoặc dùng model phát hiện ngôn ngữ cố định riêng trước khi giải mã.
# Decoder-only incremental training (2026-08-13)

LoRA is now restricted to decoder self-attention and encoder-attention
`q_proj`/`v_proj` modules. The encoder and its language-identification behavior
remain frozen. Training also supports balanced micro-stages and skipping the
slow Trainer generation pass; CT2 evaluation remains separate.

| Checkpoint | EN samples | VI samples | EN WER | VI WER | EN/VI language accuracy |
|---|---:|---:|---:|---:|---:|
| Current production | — | — | 12.62% | 41.99% | 100% / 100% |
| `decoder-micro1` | 32 | 32 | **7.28%** | **25.40%** | **100% / 100%** |
| `decoder-micro2` | 64 | 64 | 7.77% | 25.47% | 100% / 100% |
| `decoder-micro3` (new window, offset 32) | 32 | 32 | 6.80% | 26.42% | 100% / 100% |
| `decoder-micro4` (new window, offset 64) | 32 | 32 | 6.80% | 25.84% | 100% / 100% |
| `decoder-micro5-vi` (Vietnamese-only) | 0 | 32 | 7.28% | 26.49% | 100% / 100% |
| `decoder-micro6` (new window, offset 96) | 32 | 32 | 7.28% | 25.91% | 100% / 100% |
| `decoder-micro7-en` (EN-only, offset 96) | 32 | 0 | 7.28% | 25.47% | 100% / 100% |
| `decoder-micro8-en` (EN-only, offset 128) | 32 | 0 | 7.77% | 26.86% | 100% / 100% |

Decision: retain `decoder-micro1-whisper-small-ct2` as the best candidate.
Do not continue from micro2 because both language WERs regressed slightly.
Micro3 and micro4 improved English but regressed Vietnamese. A low-rate
Vietnamese-only micro5 stage also regressed Vietnamese, so it was rejected.
Micro6, micro7, and micro8 used previously unseen stage1 windows and lower
learning rates, but none beat the deployed language-specialist pair. Further
training on this same manifest is stopped to avoid overfitting. The next useful
training input must be newly recorded, consented one-micro classroom speech
with verified transcripts, especially Vietnamese accent/error cases.
The selected candidate is deployed as
`backend/ai-service/whisper-decoder-micro1-ct2`. The previous
`whisper-multi-accent-ct2` directory remains available as an automatic fallback.

Runtime specialization: `decoder-micro1` remains the Vietnamese and language
detection model (VI WER 25.40%). English accurate/final decoding is routed to
`decoder-micro4` (EN WER 6.80%). Language is detected once by the primary model
and then forced during specialist decoding to prevent EN/VI label flipping.
