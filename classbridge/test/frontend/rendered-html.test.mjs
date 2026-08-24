import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

async function render() {
  const workerUrl = new URL("../../frontend/dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request("http://localhost/", { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the ClassBridge transcription workspace", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);

  const html = await response.text();
  assert.match(html, /<title>ClassBridge — AI Teacher Assistant<\/title>/i);
  assert.match(html, /Bắt đầu phiên dịch/);
  assert.match(html, /Phụ đề trực tiếp/);
  assert.match(html, /Tự động hoàn toàn Anh ↔ Việt/);
  assert.match(html, /Âm thanh gốc được xóa ngay sau khi xử lý/);
  assert.doesNotMatch(html, /codex-preview|react-loading-skeleton/i);
});

test("implements realtime ASR-first streaming with an isolated translation tail", async () => {
  const [
    page,
    studentPage,
    pcmProcessor,
    aiService,
    streamRoute,
    sessionManager,
    runtimeSupervisor,
    trainer,
    manifestPreparer,
    globalStyles,
  ] = await Promise.all([
    readFile(new URL("../../frontend/app/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../../frontend/app/join/[code]/page.tsx", import.meta.url), "utf8"),
    readFile(new URL("../../frontend/public/pcm-processor.js", import.meta.url), "utf8"),
    readFile(new URL("../../backend/ai-service/main.py", import.meta.url), "utf8"),
    readFile(new URL("../../frontend/app/api/stream/start/route.ts", import.meta.url), "utf8"),
    readFile(new URL("../../backend/ai-service/session_manager.py", import.meta.url), "utf8"),
    readFile(new URL("../../frontend/scripts/run-local.mjs", import.meta.url), "utf8"),
    readFile(new URL("../../training/finetune_whisper_lora.py", import.meta.url), "utf8"),
    readFile(new URL("../../training/prepare_multilingual_manifest.py", import.meta.url), "utf8"),
    readFile(new URL("../../frontend/app/globals.css", import.meta.url), "utf8"),
  ]);

  // Browser audio is a continuous, normalized 16 kHz stream.
  assert.match(page, /new AudioWorkletNode/);
  assert.match(page, /new WebSocket/);
  assert.match(page, /streamingModeRef/);
  assert.match(page, /startingRef\.current/);
  assert.match(page, /Mỗi máy chỉ được sử dụng một microphone/);
  assert.match(page, /captureRuntimesRef\.current\.size > 0/);
  assert.match(page, /activeTurn\?\.sourceLanguage === result\.source_language/);
  assert.match(page, /languageChanged/);
  assert.match(page, /AUTO_LINE_BREAK_SILENCE_MS/);
  assert.match(page, /word-document source-document/);
  assert.match(page, /document-segment live-segment/);
  assert.match(page, /item\.source \|\| item\.stableText \|\| item\.unstableText/);
  assert.doesNotMatch(page, /title="Xóa câu này"/);
  assert.doesNotMatch(page, /voiceprint|speakerEmbedding/);
  assert.match(globalStyles, /\.unstable-text, \.stable-text \{ opacity: 1;/);
  assert.doesNotMatch(globalStyles, /\.unstable-text \{ opacity: 0\./);
  assert.match(page, /!streamingModeRef\.current/);
  assert.match(page, /STREAM_PING_INTERVAL_MS/);
  assert.match(pcmProcessor, /targetSampleRate = 16000/);
  assert.match(pcmProcessor, /phaseStep = this\.targetSampleRate \/ sampleRate/);

  // REST is fallback-only; live translation arrives as a separate message.
  assert.match(page, /msg\.type === "translation"/);
  assert.match(page, /msg\.segment_id/);
  assert.match(page, /source_language", "auto"/);
  assert.doesNotMatch(page, /Anh → Việt|Việt → Anh/);
  assert.match(page, /languageLabel/);
  assert.match(studentPage, /Lời gốc/);
  assert.match(studentPage, /Bản dịch/);
  assert.match(studentPage, /language_label/);

  // The server uses 300–700 ms UI updates over a 2–5 s rolling context,
  // VAD padding, a pause-triggered accurate pass and async translation.
  assert.match(aiService, /STREAM_UPDATE_SECONDS/);
  assert.match(aiService, /STREAM_ROLLING_SECONDS/);
  assert.match(aiService, /STREAM_PRE_ROLL_SECONDS/);
  assert.match(aiService, /STREAM_POST_ROLL_SECONDS/);
  assert.match(aiService, /STREAM_FINAL_ACCURATE/);
  assert.match(aiService, /TranscriptStabilizer/);
  assert.match(aiService, /detect_language_label/);
  assert.match(aiService, /whisper_english if detected == "en" else whisper_accurate/);
  assert.match(aiService, /specialist_language = detected if language == "auto" else language/);
  assert.match(aiService, /Literal\["en", "vi", "mixed"\]/);
  assert.match(aiService, /async def translation_worker/);
  assert.match(aiService, /"type": "partial"/);
  assert.match(aiService, /"type": "final"/);
  assert.match(aiService, /"type": "translation"/);
  assert.match(aiService, /"translation": ""/);
  assert.match(aiService, /translation_queue\.join\(\)/);
  assert.match(aiService, /apply_translation_glossary/);
  assert.match(aiService, /TRANSLATION_COURSE_CONTEXT/);
  assert.match(aiService, /"opus_en_vi" if source_language == "en" else "opus_vi_en"/);
  assert.match(aiService, /raw\.get\("type"\) == "websocket\.disconnect"/);

  const finalOriginalPosition = aiService.indexOf('await send_teacher(final_msg)');
  const translationEnqueuePosition = aiService.indexOf('await translation_queue.put({');
  assert.ok(finalOriginalPosition >= 0);
  assert.ok(translationEnqueuePosition > finalOriginalPosition);

  // Classroom connections use a web proxy for HTTP and a configurable WSS base.
  assert.match(streamRoute, /classroom\/join/);
  assert.match(studentPage, /NEXT_PUBLIC_AI_SERVICE_URL/);
  assert.doesNotMatch(studentPage, /127\.0\.0\.1/);
  assert.match(page, /Mã lớp trực tiếp/);
  assert.match(runtimeSupervisor, /AI_HOST \|\| "0\.0\.0\.0"/);

  // Session history and viewers are cleaned up when the teacher stream ends.
  assert.match(aiService, /session_manager\.remove_session\(session_id\)/);
  assert.match(sessionManager, /async def close_students/);

  // Question Clustering is kept for the later research phase and stays off
  // the audio streaming hot path through lazy initialization.
  assert.match(aiService, /async def _get_clustering_engine/);
  assert.match(aiService, /@app\.post\("\/questions\/add"\)/);

  // Existing LoRA/data workflows remain available for the ASR research track.
  assert.match(trainer, /--language/);
  assert.match(trainer, /balance_languages/);
  assert.match(trainer, /speaker_cap/);
  assert.match(manifestPreparer, /split_by_speaker/);
});
