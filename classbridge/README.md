# DỰ ÁN CLASSBRIDGE: HỆ THỐNG TRỢ GIẢNG AI SONG NGỮ THỜI GIAN THỰC
## Tác giả: Nguyễn Sỹ Tân (MSSV: 29212449741)

ClassBridge là hệ thống trợ giảng AI thông minh, hỗ trợ nhận diện tiếng nói và dịch thuật song ngữ (Anh - Việt) trực tiếp trong các giờ giảng đường đại học, đặc biệt tối ưu cho khối ngành Công nghệ Thông tin (CNTT).

---

### 1. CẤU TRÚC THƯ MỤC CHÍNH

```text
classbridge/
├── backend/
│   └── ai-service/              # Dịch vụ AI (Port 8000) chạy GPU với kiến trúc 2 Module + NMT
├── frontend/                    # Ứng dụng Web (Port 3000) xây dựng bằng Next.js 15 & Tailwind
├── training/                    # Công cụ và kịch bản huấn luyện Fine-tune LoRA & Benchmark
├── start-classbridge.ps1        # Script PowerShell khởi động toàn bộ hệ thống bằng 1 click
└── AI_CAPSTONE_HANDBOOK.md      # Sổ tay kiến trúc giải pháp và phương pháp luận NCKH
```

---

### 2. TỔNG QUAN VAI TRÒ CỦA CÁC THÀNH PHẦN

| Thành Phần | Thư Mục | Vai Trò & Công Dụng |
| :--- | :--- | :--- |
| **Backend AI Service** | `backend/ai-service/` | Xử lý âm thanh, định tuyến ngôn ngữ (<3ms), chạy 2 module Whisper chuyên biệt trên GPU và dịch thuật EnViT5. |
| **Frontend Web** | `frontend/` | Giao diện thu âm mic/tab, hiển thị phụ đề song ngữ 2 cột thời gian thực với độ trễ cực thấp. |
| **Training Pipeline** | `training/` | Huấn luyện LoRA cho Whisper (Việt/Anh) và EnViT5, xuất sang CTranslate2, đánh giá WER/BLEU. |

---

### 3. CÁCH CHẠY HỆ THỐNG (QUICK START)

1. **Khởi động nhanh bằng script:**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\start-classbridge.ps1
   ```
2. **Hoặc khởi động từng phần:**
   - **Backend:**
     ```powershell
     cd backend/ai-service
     .venv\Scripts\python.exe main.py
     ```
   - **Frontend:**
     ```powershell
     cd frontend
     npm run dev
     ```
   Truy cập web: `http://localhost:3000`.
