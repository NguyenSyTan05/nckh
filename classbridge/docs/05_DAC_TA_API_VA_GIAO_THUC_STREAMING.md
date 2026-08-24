# 05. Đặc Tả API & Giao Thức Streaming (API & Streaming Protocol Specification)

---

## 1. Giao Thức WebSocket Thời Gian Thực (WebSocket Real-Time Streaming)

Kết nối WebSocket phục vụ truyền nhận luồng âm thanh micro từ giảng viên và phát sóng phụ đề/dịch thuật tới tất cả học viên.

### 1.1. Endpoints WebSocket
- **Phòng học / Lớp học**: `ws://localhost:8000/ws/classroom/{join_code}`
- **Phiên xử lý riêng lẻ**: `ws://localhost:8000/ws/stream/{session_id}`

---

### 1.2. Định Dạng Gói Tin: Client ➔ Server (JSON Text Frames)

#### Gói tin gửi đoạn âm thanh (`audio_chunk`):
```json
{
  "type": "audio_chunk",
  "mic_id": "teacher",
  "seq": 101,
  "fmt": "pcm16",
  "sample_rate": 16000,
  "data": "<base64_encoded_pcm16_data>"
}
```

#### Gói tin báo hiệu giọng nói (`vad`):
```json
{
  "type": "vad",
  "mic_id": "teacher",
  "event": "start" | "pause" | "end"
}
```

#### Gói tin giữ kết nối (`ping`):
```json
{
  "type": "ping"
}
```

---

### 1.3. Định Dạng Gói Tin: Server ➔ Client (Broadcast)

#### Phụ đề tạm thời thời gian thực (`partial_transcript`):
```json
{
  "type": "partial_transcript",
  "mic_id": "teacher",
  "seq": 101,
  "partial": "Hôm nay chúng ta sẽ tìm hiểu về mô hình Transformer..."
}
```

#### Phụ đề hoàn chỉnh chốt câu (`final_transcript`):
```json
{
  "type": "final_transcript",
  "mic_id": "teacher",
  "text": "Hôm nay chúng ta sẽ tìm hiểu về mô hình Transformer trong AI.",
  "language": "VI",
  "confidence": 0.96
}
```

#### Bản dịch song ngữ tương ứng (`translation`):
```json
{
  "type": "translation",
  "mic_id": "teacher",
  "text": "Today we will learn about the Transformer model in AI.",
  "source_language": "VI",
  "target_language": "EN"
}
```

#### Phản hồi kết nối (`pong`):
```json
{
  "type": "pong"
}
```

---

## 2. Đặc Tả REST API (HTTP Endpoints)

### 2.1. Kiểm Tra Trạng Thái Hệ Thống (Health Check)
- **Endpoint**: `GET /health`
- **Response**:
```json
{
  "status": "ok",
  "device": "cuda",
  "model_loaded": "whisper-decoder-micro1-ct2",
  "active_sessions": 3
}
```

---

### 2.2. Nhận Dạng File Âm Thanh Độc Lập (Batch ASR)
- **Endpoint**: `POST /v1/transcribe`
- **Content-Type**: `multipart/form-data`
- **Tham số**:
  - `file`: File âm thanh (`.wav`, `.mp3`, `.m4a`)
  - `language`: `vi` | `en` | `auto` (Mặc định `auto`)
- **Response**:
```json
{
  "text": "Kiểm thử phần mềm giúp nâng cao chất lượng ứng dụng.",
  "language": "vi",
  "duration_seconds": 3.45
}
```

---

### 2.3. Dịch Thuật Văn Bản Trực Tiếp (NMT Translation)
- **Endpoint**: `POST /v1/translate` hoặc `POST /api/translate`
- **Request Body**:
```json
{
  "text": "Convolutional Neural Network is widely used in Computer Vision.",
  "source_lang": "en",
  "target_lang": "vi"
}
```
- **Response**:
```json
{
  "translated_text": "Mạng nơ-ron tích chập được sử dụng rộng rãi trong Thị giác máy tính.",
  "source_lang": "en",
  "target_lang": "vi"
}
```

---

### 2.4. Quản Lý & Gom Cụm Câu Hỏi (Question Clustering API)

#### Gửi câu hỏi mới:
- **Endpoint**: `POST /questions/add`
- **Request Body**:
```json
{
  "session_id": "CLASS_IT101_2026",
  "student_id": "SV12345",
  "student_name": "Nguyen Van A",
  "question": "Thầy cho em hỏi cơ chế Self-Attention khác gì so với Attention truyền thống ạ?"
}
```

#### Lấy danh sách các cụm câu hỏi:
- **Endpoint**: `GET /questions/clusters/{session_id}`
- **Response**:
```json
{
  "session_id": "CLASS_IT101_2026",
  "total_questions": 18,
  "clusters": [
    {
      "cluster_id": 1,
      "topic": "Cơ chế Attention & Transformer",
      "count": 7,
      "representative_question": "Cơ chế Self-Attention hoạt động như thế nào?",
      "questions": [
        {"id": "q1", "text": "Thầy giải thích thêm về ma trận Q, K, V?", "author": "Nguyen Van A"},
        {"id": "q4", "text": "Self-attention có tính toán song song được không?", "author": "Tran Thi B"}
      ]
    },
    {
      "cluster_id": 2,
      "topic": "Hạn chót nộp bài tập lớn",
      "count": 4,
      "representative_question": "Hạn nộp báo cáo NCKH là khi nào?",
      "questions": [...]
    }
  ]
}
```
