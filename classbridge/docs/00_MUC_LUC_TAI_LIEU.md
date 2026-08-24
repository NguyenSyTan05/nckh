# Bộ Tài Liệu Kỹ Thuật Hệ Thống ClassBridge AI
**Hệ Thống Trợ Giảng & Dịch Thuật Bài Giảng Song Ngữ Thời Gian Thực**

---

## 📌 Giới Thiệu
Thư mục `docs/` chứa toàn bộ tài liệu kỹ thuật, kiến trúc hệ thống, tài liệu huấn luyện AI và hướng dẫn vận hành của dự án **ClassBridge** (Tài liệu Nghiên Cứu Khoa Học).

---

## 📑 Danh Mục Tài Liệu

| STT | Tài Liệu | Mô Tả Tóm Tắt |
|:---:|:---|:---|
| **01** | [**01. Tổng Quan & Kiến Trúc Hệ Thống**](./01_TONG_QUAN_VA_KIEN_TRUC_HE_THONG.md) | Giới thiệu dự án, bài toán giải quyết, kiến trúc tổng thể (Frontend, Backend, AI Service) và luồng dữ liệu thời gian thực. |
| **02** | [**02. Kiến Trúc AI & Pipeline Xử Lý**](./02_KIEN_TRUC_AI_VA_PIPELINE_XU_LY.md) | Chi tiết các module AI cốt lõi: Whisper CTranslate2 ASR, LoRA Fine-Tuning, NMT dịch thuật học thuật, Transcript Stabilizer, Auto Punctuation, Correction Memory và Question Clustering. |
| **03** | [**03. Hướng Dẫn Cài Đặt & Vận Hành**](./03_HUONG_DAN_CAI_DAT_VA_VAN_HANH.md) | Yêu cầu phần cứng (NVIDIA CUDA), môi trường Python & Node.js, cấu hình biến môi trường và hướng dẫn khởi chạy các chế độ qua script điều khiển. |
| **04** | [**04. Quy Trình Huấn Luyện & Tối Ưu AI**](./04_QUY_TRINH_HUAN_LUYEN_VA_TOI_UU_AI.md) | Hướng dẫn chuẩn bị dữ liệu (VIVOS, ViMD, DTU vocab), quy trình Fine-tune LoRA decoder-only, xuất mô hình CTranslate2 INT8 và báo cáo thực nghiệm WER/BLEU. |
| **05** | [**05. Đặc Tả API & Giao Thức Streaming**](./05_DAC_TA_API_VA_GIAO_THUC_STREAMING.md) | Đặc tả kỹ thuật các REST API endpoints và định dạng gói tin WebSocket thời gian thực (Audio PCM16 streaming, Partial/Final transcript, Live translation). |
| **06** | [**06. Luồng Xử Lý Chi Tiết & Hướng Phát Triển**](./06_LUONG_XU_LY_VA_HUONG_PHAT_TRIEN.md) | Sơ đồ tuần tự End-to-End luồng xử lý âm thanh ➔ phụ đề ➔ dịch thuật và lộ trình định hướng phát triển NCKH tương lai (Diarization, Code-Switching, RAG LLM). |

---

## 🎯 Cấu Trúc Thư Mục Dự Án
```text
classbridge/
├── backend/
│   ├── ai-service/          # Service xử lý AI chính (FastAPI, Whisper CT2, NMT, WebSocket)
│   ├── data/                # Dữ liệu cục bộ & SQLite/D1
│   ├── db/                  # Định nghĩa ORM (Drizzle)
│   └── start-classbridge-ai.ps1
├── frontend/                # Ứng dụng Web Client (Next.js / Vinext, React 19, TailwindCSS)
├── training/                # Bộ công cụ huấn luyện, fine-tune và đánh giá mô hình AI
├── docs/                    # Tài liệu kỹ thuật hệ thống (Bộ tài liệu này)
├── start-classbridge.ps1     # Script điều khiển Master khởi chạy ứng dụng & train
└── package.json             # NPM scripts điều phối
```
