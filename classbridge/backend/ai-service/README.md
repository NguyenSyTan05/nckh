# THƯ MỤC: classbridge/backend/ai-service/
## Phân Hệ Backend AI-Service (Dịch Vụ Trí Tuệ Nhân Tạo Thời Gian Thực)

**Tác giả:** Nguyễn Sỹ Tân  
**Kiến trúc:** Kiến trúc Tinh Gọn (Unified Multilingual ASR + Meta NLLB-200)  
**Cổng phục vụ:** Port 8000  

---

### 1. CÔNG DỤNG CHÍNH CỦA THƯ MỤC
Thư mục này chứa toàn bộ mã nguồn Backend AI chịu trách nhiệm:
1. Nạp và vận hành 2 mô hình học sâu cốt lõi trên GPU CUDA (tiết kiệm VRAM cho card RTX 3050 4GB).
2. Nhận diện giọng nói đa ngữ (Tiếng Việt, Tiếng Anh & Code-switching CNTT) qua giao thức WebSocket và REST API.
3. Dịch thuật song ngữ tự động 2 chiều (Việt ↔ Anh) bằng mô hình Meta NLLB-200.
4. Cung cấp API trích xuất đặc trưng ngữ nghĩa và tính độ tương đồng câu hỏi dùng chung cho tính năng **Gom cụm câu hỏi (Question Clustering)**.

---

### 2. DANH SÁCH CHI TIẾT CÁC TỆP TIN & THƯ MỤC CON

| Tên File / Thư mục | Công Dụng Chi Tiết | Có Cần Thiết Không? |
| :--- | :--- | :---: |
| **`main.py`** | Server FastAPI chính: Chứa API `/transcribe`, `/translate`, `/ask_qa` và WebSocket `/ws/transcribe`. Quản lý VAD, kết nối các module AI. | **BẮT BUỘC** (Trọng tâm) |
| **`unified_speech_recognizer.py`** | Module nhận dạng giọng nói đa ngữ thống nhất (Whisper CTranslate2 Float16). | **BẮT BUỘC** |
| **`04_TRANSLATION_MODULE/`** | Module Dịch thuật & Ngữ nghĩa: Sử dụng Meta NLLB-200 (Distilled-600M) dịch 2 chiều và tính tương đồng câu hỏi. | **BẮT BUỘC** |
| **`nmt-academic-lora-balanced/`** | Trọng số LoRA của mô hình dịch thuật học thuật EnViT5 (offline fallback). | **BẮT BUỘC** |
| **`.models/`** | Cache cục bộ của mô hình faster-whisper-small (offline inference). | **BẮT BUỘC** |
| **`requirements.txt`** | Danh sách các thư viện Python cần thiết (`fastapi`, `faster-whisper`, `transformers`, `torch`, `peft`...). | **BẮT BUỘC** |
| **`training/Module_Train/`** | Toàn bộ module huấn luyện, chuẩn bị/tách dữ liệu và xuất CTranslate2 đã được tập trung tại phân hệ `classbridge/training/Module_Train/`. | **TẬP TRUNG TẠI TRAINING** |
| **`HUONG_DAN_QUY_TRINH_TOAN_BO.md`**| Sổ tay hướng dẫn quy trình huấn luyện và vận hành tổng thể. | **CẦN THIẾT** (Tham khảo) |
| **`start_ai.ps1`** / **`start_ai.cmd`** | Script 1-click khởi chạy server AI trên cổng 8000. | **TIỆN ÍCH** |

---

### 3. CÁCH KHỞI ĐỘNG DỊCH VỤ
```powershell
cd d:\TailieuNPKH\classbridge\backend\ai-service
.\.venv\Scripts\python.exe main.py
```
Dịch vụ sẵn sàng khi xuất hiện thông báo:
`Application startup complete. Uvicorn running on http://127.0.0.1:8000`
