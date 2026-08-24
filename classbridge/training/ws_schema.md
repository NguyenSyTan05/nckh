WebSocket message schema for ClassBridge ASR scaffold

Client -> Server messages (JSON text frames)

1) audio_chunk
{
  "type": "audio_chunk",
  "mic_id": "teacher",          # logical source id
  "seq": 123,                    # incremental sequence number
  "fmt": "pcm16",              # format (pcm16 expected)
  "sample_rate": 16000,
  "data": "<base64-encoded-pcm16>"
}

2) vad event
{
  "type": "vad",
  "mic_id": "teacher",
  "event": "start"|"pause"|"end"
}

3) ping
{ "type": "ping" }


Server -> Client messages (JSON text frames)

1) partial_transcript
{
  "type": "partial_transcript",
  "mic_id": "teacher",
  "seq": 123,
  "partial": "Today we will learn..."
}

2) final_transcript
{
  "type": "final_transcript",
  "mic_id": "teacher",
  "text": "Today we will learn about software testing.",
  "language": "EN"    # EN|VI|MIXED
}

3) translation
{
  "type": "translation",
  "mic_id": "teacher",
  "text": "Hôm nay chúng ta sẽ học về kiểm thử phần mềm.",
  "source_language": "EN"
}

4) pong
{ "type": "pong" }

Notes / extension points:
- For production, send timestamps, token-level offsets, confidence scores and stable/unstable boundaries.
- Consider binary frames for audio to avoid base64 overhead. For that, use an initial JSON meta frame indicating seq and mic_id, followed by raw binary.
- Include message `trace_id` or `utterance_id` to let client align partials/final messages reliably.
