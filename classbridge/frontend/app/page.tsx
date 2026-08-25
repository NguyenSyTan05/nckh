"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type Subtitle = {
  id: string;
  segmentId?: number;
  revision?: number;
  final?: boolean;
  source: string;
  stableText?: string;
  unstableText?: string;
  isPartial?: boolean;
  translated: string;
  sourceLanguage: "en" | "vi";
  languageLabel?: "en" | "vi" | "mixed";
  latencyMs: number;
  createdAt: string;
};

type ApiResult = {
  transcript: string;
  corrected_text: string;
  source_language: "en" | "vi";
  latency_ms: number;
  recognition_mode: "fast" | "accurate";
  confidence: number;
  demo?: boolean;
};

type TranslationResult = { translation: string; error?: string; detail?: string };
type TranslationJob = {
  id: string;
  text: string;
  sourceLanguage: "en" | "vi";
};
type ActiveTurn = {
  subtitleId: string;
  source: string;
  sourceLanguage: "en" | "vi";
};
type AudioKind = "quiet" | "background" | "speech";
type AudioSource = "microphone" | "tab";
type MicrophoneOption = { deviceId: string; label: string };
type AudioChunk = {
  blob: Blob;
  endedByPause: boolean;
  startsNewTurn: boolean;
};
type CaptureRuntime = {
  stream: MediaStream;
  audioContext: AudioContext;
  recorder: MediaRecorder | null;
  meterTimer: number | null;
  segmentTimer: number | null;
  audioKind: AudioKind;
};

type StreamMetadata = {
  session_id: string;
  join_code?: string;
  ws_url?: string;
};

const LIVE_DRAFT_STORAGE_KEY = "classbridge_live_subtitle_draft";

const mimeCandidates = [
  "audio/webm;codecs=opus",
  "audio/webm",
  "audio/mp4",
];
const AUDIO_METER_INTERVAL_MS = 60;
const MIN_UTTERANCE_MS = 160;
const END_OF_UTTERANCE_SILENCE_MS = 2_500;
// A pause closes the current display line. This also acts as the anonymous
// turn boundary when another person starts speaking; no speaker identity or
// biometric voice data is collected.
const AUTO_LINE_BREAK_SILENCE_MS = END_OF_UTTERANCE_SILENCE_MS;
// REST is only a fallback, but it must retain a complete Vietnamese clause.
// Short 3–4 second recordings were frequently decoded with words missing.
const MAX_HYBRID_UTTERANCE_MS = 8_000;
const MAX_PLAYBACK_UTTERANCE_MS = 7_000;
const MAX_PARALLEL_TRANSCRIPTIONS = 3;
const MAX_LINE_CHARACTERS = 1_200;
const SOFT_LINE_WORDS = 80;
const STREAM_CONNECT_TIMEOUT_MS = 4_000;
const STREAM_PING_INTERVAL_MS = 15_000;

function getAiBaseUrl(): string {
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (host === "localhost" || host === "127.0.0.1" || host === "0.0.0.0" || host.startsWith("192.168.") || host.startsWith("10.") || host.startsWith("172.")) {
      return `http://${host}:8000`;
    }
  }
  const configured = process.env.NEXT_PUBLIC_AI_SERVICE_URL?.trim();
  if (configured) return configured.replace(/\/+$/, "");
  return "";
}

function buildAiWebSocketUrl(pathname: string) {
  const base = getAiBaseUrl();
  const url = base ? new URL(base, window.location.href) : new URL(window.location.href);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  if (!base) url.port = "8000";
  url.pathname = pathname.startsWith("/") ? pathname : `/${pathname}`;
  url.search = "";
  url.hash = "";
  return url.toString();
}

function normalizedWord(word: string) {
  return word.toLocaleLowerCase().replace(/^[^\p{L}\p{N}]+|[^\p{L}\p{N}]+$/gu, "");
}

function isSentenceEnd(text: string): boolean {
  const t = text.trimEnd();
  return /[.!?]$/.test(t) || /[,;]$/.test(t);
}

function wordCount(text: string): number {
  return text.trim() === "" ? 0 : text.trim().split(/\s+/).length;
}

function mergeTranscript(previous: string, incoming: string) {
  const left = previous.trim().replace(/\s+/g, " ");
  const right = incoming.trim().replace(/\s+/g, " ");
  if (!left) return right;
  if (!right) return left;
  if (left.includes(right)) return left;
  if (right.includes(left)) return right;
  return right;
}


function visibleSourceText(item: Subtitle) {
  return (item.source || item.stableText || item.unstableText || "").trim();
}

function pickMimeType() {
  return mimeCandidates.find((type) => MediaRecorder.isTypeSupported(type)) ?? "";
}

function clock(iso: string) {
  return new Intl.DateTimeFormat("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  }).format(new Date(iso));
}

type TranslationMode = "auto" | "vi" | "en";

type LectureSession = {
  id: string;
  title: string;
  createdAt: string;
  endedAt: string;
  durationSeconds: number;
  subtitles: Subtitle[];
  translationMode: TranslationMode;
};

export default function Home() {
  const [recording, setRecording] = useState(false);
  const [sessionState, setSessionState] = useState<"idle" | "starting" | "recording" | "paused" | "ended">("idle");
  const [translationMode, setTranslationMode] = useState<TranslationMode>("auto");
  const [sessionDuration, setSessionDuration] = useState<number>(0);
  const [lectureHistory, setLectureHistory] = useState<LectureSession[]>([]);
  const [showHistoryModal, setShowHistoryModal] = useState<boolean>(false);
  const [selectedHistorySession, setSelectedHistorySession] = useState<LectureSession | null>(null);
  const [micPermissionPrompt, setMicPermissionPrompt] = useState<boolean>(false);
  const [classroomJoinCode, setClassroomJoinCode] = useState<string>("");
  const timerRef = useRef<number | null>(null);
  const sessionStartTimeRef = useRef<number>(0);

  const [starting, setStarting] = useState(false);
  const startingRef = useRef(false);
  const [audioSource, setAudioSource] = useState<AudioSource>("microphone");
  const [microphones, setMicrophones] = useState<MicrophoneOption[]>([]);
  const [selectedMicrophoneId, setSelectedMicrophoneId] = useState("");
  const [subtitles, setSubtitles] = useState<Subtitle[]>([]);
  const [viewMode, setViewMode] = useState<"lines" | "document">("lines");
  const [status, setStatus] = useState("Sẵn sàng bắt đầu");
  const [error, setError] = useState("");
  const [audioKind, setAudioKind] = useState<AudioKind>("quiet");
  const captureRuntimesRef = useRef(new Map<string, CaptureRuntime>());
  const recordingActiveRef = useRef(false);
  const queueRef = useRef<AudioChunk[]>([]);
  const processingRef = useRef(false);
  const translationQueueRef = useRef<TranslationJob[]>([]);
  const translationProcessingRef = useRef(false);
  const translationAbortRef = useRef<AbortController | null>(null);
  const sessionIdRef = useRef(0);
  const transcribeAbortRef = useRef(new Set<AbortController>());
  const audioSourceRef = useRef(audioSource);
  const subtitlesRef = useRef<Subtitle[]>([]);
  const activeTurnRef = useRef<ActiveTurn | null>(null);
  const segmentStateRef = useRef(new Map<string, { lastRevision: number; finalCommitted: boolean }>());
  const expectedChunkIdRef = useRef<number>(1);
  const packetBufferRef = useRef<Map<number, any>>(new Map());
  const audioKindRef = useRef<AudioKind>("quiet");
  const englishPanelRef = useRef<HTMLDivElement | null>(null);
  const vietnamesePanelRef = useRef<HTMLDivElement | null>(null);
  const userScrolledUpRef = useRef<{ en: boolean; vi: boolean }>({ en: false, vi: false });
  const [isScrolledUp, setIsScrolledUp] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);
  const wsPingTimerRef = useRef<number | null>(null);
  const streamingModeRef = useRef(false);
  const draftSaveTimerRef = useRef<number | null>(null);
  const scrollFrameRef = useRef<number | null>(null);

  const handlePanelScroll = useCallback((panelType: "en" | "vi", el: HTMLDivElement | null) => {
    if (!el) return;
    const distanceFromBottom = el.scrollHeight - el.scrollTop - el.clientHeight;
    const isUp = distanceFromBottom > 60;
    userScrolledUpRef.current[panelType] = isUp;
    setIsScrolledUp(userScrolledUpRef.current.en || userScrolledUpRef.current.vi);
  }, []);

  const scrollToBottom = useCallback(() => {
    userScrolledUpRef.current = { en: false, vi: false };
    setIsScrolledUp(false);
    for (const panel of [englishPanelRef.current, vietnamesePanelRef.current]) {
      if (panel) {
        panel.scrollTo({ top: panel.scrollHeight, behavior: "smooth" });
      }
    }
  }, []);

  const refreshMicrophones = useCallback(async () => {
    if (!navigator.mediaDevices?.enumerateDevices) return;
    const devices = await navigator.mediaDevices.enumerateDevices();
    const inputs = devices
      .filter((device) => device.kind === "audioinput")
      .map((device, index) => ({
        deviceId: device.deviceId,
        label: device.label || `Microphone ${index + 1}`,
      }));
    setMicrophones(inputs);
    setSelectedMicrophoneId((current) =>
      current && inputs.some((input) => input.deviceId === current)
        ? current
        : inputs[0]?.deviceId || "",
    );
  }, []);

  const processSinglePacket = useCallback((msg: any) => {
    const sessionId = typeof msg.session_id === "string" ? msg.session_id : "global";
    const segmentId = Number(msg.segment_id) || 0;
    const revision = Number(msg.revision) || 0;
    const isFinal = Boolean(msg.final || msg.type === "final");
    const rawText = (msg.text || msg.transcript || "").trim();
    const stableText = (msg.stable_text || "").trim();
    const unstableText = msg.unstable_text || "";
    const lang: "en" | "vi" = msg.language === "en" ? "en" : "vi";
    const langLabel = msg.language_label || lang;
    const latencyMs = Number(msg.latency_ms) || 0;

    if (!segmentId) return;
    if (!rawText && !isFinal) return;

    const stateKey = `${sessionId}:${segmentId}`;
    const prior = segmentStateRef.current.get(stateKey) ?? { lastRevision: 0, finalCommitted: false };

    // RULE 7: Final Lock – Nếu segment đã final thì bỏ qua mọi partial cũ
    if (prior.finalCommitted && !isFinal) {
      return;
    }
    // RULE 6 & 12: Chống duplicate revision hoặc revision cũ hơn
    if (revision <= prior.lastRevision && !isFinal) {
      return;
    }

    prior.lastRevision = Math.max(prior.lastRevision, revision);
    if (isFinal) {
      prior.finalCommitted = true;
    }
    segmentStateRef.current.set(stateKey, prior);

    const subtitleId = `seg_${segmentId}`;

    setSubtitles((prev) => {
      const index = prev.findIndex((s) => s.id === subtitleId || s.segmentId === segmentId);
      if (index === -1) {
        if (!rawText) return prev;
        // RULE 9: Tạo segment mới
        return [
          ...prev,
          {
            id: subtitleId,
            segmentId,
            revision,
            final: isFinal,
            isPartial: !isFinal,
            source: rawText,
            stableText: isFinal ? rawText : stableText,
            unstableText: isFinal ? "" : unstableText,
            translated: isFinal && msg.translation ? String(msg.translation).trim() : "",
            sourceLanguage: lang,
            languageLabel: langLabel,
            latencyMs,
            createdAt: new Date().toISOString(),
          },
        ];
      }

      const existing = prev[index];
      // RULE 7: Không cho partial cũ ghi đè lên segment đã final
      if (existing.final && !isFinal) {
        return prev;
      }

      const next = [...prev];
      const nextSource = rawText || existing.source;
      if (!nextSource.trim()) {
        return prev;
      }

      next[index] = {
        ...existing,
        revision: Math.max(existing.revision || 0, revision),
        final: isFinal || existing.final,
        isPartial: !isFinal && !existing.final,
        source: nextSource,
        stableText: isFinal ? nextSource : stableText,
        unstableText: isFinal ? "" : unstableText,
        translated: msg.translation ? String(msg.translation).trim() : existing.translated,
        sourceLanguage: lang,
        languageLabel: langLabel,
        latencyMs: latencyMs || existing.latencyMs,
      };
      return next;
    });

    if (isFinal) {
      setStatus("Đã xuống dòng • đang dịch song ngữ");
    } else {
      setStatus(`Đang nhận dạng trực tiếp • ${lang === "en" ? "tiếng Anh" : "tiếng Việt"}`);
    }
  }, []);

  const handleWsMessage = useCallback((event: MessageEvent) => {
    try {
      const msg = JSON.parse(event.data);
      if (msg.type === "pong") return;
      if (msg.type === "session_end") {
        setStatus("Đã hoàn tất lời gốc và các bản dịch cuối cùng");
        return;
      }
      if (msg.type === "translation") {
        const trans = String(msg.translation || "").trim();
        if (!trans) return;
        const segmentId = Number(msg.segment_id);
        const subtitleId = `seg_${segmentId}`;
        setSubtitles((prev) =>
          prev.map((item) =>
            item.id === subtitleId || item.segmentId === segmentId
              ? { ...item, translated: trans }
              : item,
          ),
        );
        return;
      }

      // Xử lý gói tin ASR / Subtitle ngay lập tức (0ms buffer delay)
      processSinglePacket(msg);
    } catch (err) {
      console.error("WS message parse error", err);
    }
  }, [processSinglePacket]);

  useEffect(() => {
    if (sessionState === "recording") {
      timerRef.current = window.setInterval(() => {
        setSessionDuration((prev) => prev + 1);
      }, 1000);
    } else if (sessionState !== "paused" && timerRef.current !== null) {
      window.clearInterval(timerRef.current);
      timerRef.current = null;
    }
    return () => {
      if (timerRef.current !== null) window.clearInterval(timerRef.current);
    };
  }, [sessionState]);

  useEffect(() => {
    const frame = window.requestAnimationFrame(() => {
      try {
        const saved = localStorage.getItem("classbridge_lecture_history");
        if (saved) setLectureHistory(JSON.parse(saved));
        // Luôn bắt đầu với màn hình trống sạch 100%, không tự nạp lại câu nháp cũ
        localStorage.removeItem(LIVE_DRAFT_STORAGE_KEY);
      } catch (err) {
        console.error("Failed to load lecture history", err);
      }
      void refreshMicrophones().catch(() => undefined);
    });
    const onDeviceChange = () => void refreshMicrophones().catch(() => undefined);
    navigator.mediaDevices?.addEventListener?.("devicechange", onDeviceChange);
    return () => {
      window.cancelAnimationFrame(frame);
      navigator.mediaDevices?.removeEventListener?.("devicechange", onDeviceChange);
    };
  }, [refreshMicrophones]);

  function formatDuration(seconds: number) {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    if (hrs > 0) {
      return `${hrs.toString().padStart(2, "0")}:${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
    }
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  }

  useEffect(() => {
    audioSourceRef.current = audioSource;
  }, [audioSource]);

  useEffect(() => {
    subtitlesRef.current = subtitles;
    if (scrollFrameRef.current !== null) {
      window.cancelAnimationFrame(scrollFrameRef.current);
    }
    scrollFrameRef.current = window.requestAnimationFrame(() => {
      scrollFrameRef.current = null;
      if (englishPanelRef.current && !userScrolledUpRef.current.en) {
        englishPanelRef.current.scrollTop = englishPanelRef.current.scrollHeight;
      }
      if (vietnamesePanelRef.current && !userScrolledUpRef.current.vi) {
        vietnamesePanelRef.current.scrollTop = vietnamesePanelRef.current.scrollHeight;
      }
    });

    // Partial captions arrive several times per second. Persist the newest
    // snapshot at most once per 750 ms instead of serializing the full lecture
    // on every word update.
    if (draftSaveTimerRef.current === null) {
      draftSaveTimerRef.current = window.setTimeout(() => {
        draftSaveTimerRef.current = null;
        try {
          const latest = subtitlesRef.current;
          if (latest.length > 0) {
            localStorage.setItem(LIVE_DRAFT_STORAGE_KEY, JSON.stringify(latest));
          } else {
            localStorage.removeItem(LIVE_DRAFT_STORAGE_KEY);
          }
        } catch (err) {
          console.error("Failed to save live subtitle draft", err);
        }
      }, 750);
    }
  }, [subtitles]);

  useEffect(() => () => {
    if (draftSaveTimerRef.current !== null) window.clearTimeout(draftSaveTimerRef.current);
    if (scrollFrameRef.current !== null) window.cancelAnimationFrame(scrollFrameRef.current);
  }, []);

  const processTranslationQueue = useCallback(async () => {
    if (translationProcessingRef.current) return;
    translationProcessingRef.current = true;

    while (translationQueueRef.current.length > 0) {
      const job = translationQueueRef.current.shift();
      if (!job) continue;

      const trimmedText = job.text.trim();
      if (!trimmedText) continue;

      const controller = new AbortController();
      translationAbortRef.current = controller;

      try {
        const base = getAiBaseUrl();
        const translateUrl = base ? `${base}/v1/translate` : "/api/translate";
        const response = await fetch(translateUrl, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            text: trimmedText,
            source_language: job.sourceLanguage,
          }),
          signal: controller.signal,
        });
        const translated = (await response.json()) as TranslationResult;
        if (!response.ok) {
          throw new Error(translated.error || translated.detail || "Không thể dịch nội dung");
        }
        if (translated.translation?.trim()) {
          setSubtitles((items) =>
            items.map((item) =>
              item.id === job.id
                ? { ...item, translated: translated.translation.trim() }
                : item,
            ),
          );
        }
      } catch (cause) {
        if (!(cause instanceof DOMException && cause.name === "AbortError")) {
          setError(cause instanceof Error ? cause.message : "Không thể dịch nội dung");
        }
      }
    }

    translationAbortRef.current = null;
    translationProcessingRef.current = false;
  }, []);

  const processQueue = useCallback(async () => {
    if (processingRef.current || queueRef.current.length === 0) return;
    processingRef.current = true;
    setStatus("Đang nhận dạng tuần tự theo lượt nói…");

    try {
      while (queueRef.current.length > 0) {
        const sessionId = sessionIdRef.current;
        const context = subtitlesRef.current
          .slice(-5)
          .map((item) => item.source)
          .join(" ")
          .slice(-360);
        const batchSize = audioSourceRef.current === "microphone"
          ? 1
          : MAX_PARALLEL_TRANSCRIPTIONS;
        const batch = queueRef.current
          .splice(0, batchSize)
          .filter((chunk) => chunk.blob.size >= 400);
        const pendingOutcomes = batch.map(async (chunk) => {
          const controller = new AbortController();
          transcribeAbortRef.current.add(controller);
          try {
            const form = new FormData();
            const audioFileName = chunk.blob.type.includes("mp4") ? "lecture.m4a" : "lecture.webm";
            form.append("audio", chunk.blob, audioFileName);
            form.append("source_language", "auto");
            const audioProfile = audioSourceRef.current === "tab" ? "music" : "hybrid";
            form.append("audio_profile", audioProfile);
            form.append("context", context);
            const base = getAiBaseUrl();
            const transcribeUrl = base ? `${base}/v1/transcribe` : "/api/transcribe";
            const response = await fetch(transcribeUrl, {
              method: "POST",
              body: form,
              signal: controller.signal,
            });
            const result = (await response.json()) as ApiResult & { error?: string; detail?: string };
            if (!response.ok) {
              throw new Error(result.error || result.detail || "Không thể xử lý âm thanh");
            }
            return {
              result,
              endedByPause: chunk.endedByPause,
              startsNewTurn: chunk.startsNewTurn,
            };
          } catch (cause) {
            return {
              cause,
              endedByPause: chunk.endedByPause,
              startsNewTurn: chunk.startsNewTurn,
            };
          } finally {
            transcribeAbortRef.current.delete(controller);
          }
        });

        for (const pendingOutcome of pendingOutcomes) {
          const outcome = await pendingOutcome;
          if (sessionId !== sessionIdRef.current) continue;
          if (outcome.cause) {
            if (outcome.endedByPause) activeTurnRef.current = null;
            if (!(outcome.cause instanceof DOMException && outcome.cause.name === "AbortError")) {
              setError(outcome.cause instanceof Error ? outcome.cause.message : "Đã xảy ra lỗi");
              setStatus("Mất kết nối dịch vụ AI");
            }
            continue;
          }

          const result = outcome.result;
          if (!result) continue;
          if (result.corrected_text.trim()) {
            const activeTurn = activeTurnRef.current;
            const currentWords = activeTurn ? wordCount(activeTurn.source) : 0;
            const lineIsHardFull = Boolean(
              activeTurn && (
                activeTurn.source.length >= MAX_LINE_CHARACTERS ||
                mergeTranscript(activeTurn.source, result.corrected_text).length > MAX_LINE_CHARACTERS
              ),
            );
            const lineIsSentenceEnd = Boolean(
              activeTurn &&
              currentWords >= SOFT_LINE_WORDS &&
              isSentenceEnd(activeTurn.source)
            );
            const lineIsFull = lineIsHardFull || lineIsSentenceEnd;
            const languageChanged = activeTurn?.sourceLanguage !== result.source_language;
            const continuesCurrentTurn =
              !outcome.startsNewTurn &&
              !lineIsFull &&
              !languageChanged &&
              activeTurn?.sourceLanguage === result.source_language &&
              activeTurn !== null;
            const previousTurnSource = continuesCurrentTurn ? activeTurn.source : "";
            const mergedSource = mergeTranscript(previousTurnSource, result.corrected_text);
            if (continuesCurrentTurn && mergedSource === previousTurnSource) {
              if (outcome.endedByPause) activeTurnRef.current = null;
              setError("");
              setStatus("Đã đồng bộ phần lời nói trùng");
              continue;
            }

            let subtitleId: string;
            if (!continuesCurrentTurn) {
              subtitleId = crypto.randomUUID();
              setSubtitles((items) => [
                ...items,
                {
                  id: subtitleId,
                  source: mergedSource,
                  translated: "",
                  sourceLanguage: result.source_language,
                  languageLabel: result.source_language,
                  latencyMs: result.latency_ms,
                  createdAt: new Date().toISOString(),
                },
              ]);
            } else {
              subtitleId = activeTurn.subtitleId;
              setSubtitles((items) => items.map((item) =>
                item.id === subtitleId
                  ? {
                      ...item,
                      source: mergedSource,
                      sourceLanguage: result.source_language,
                      languageLabel: result.source_language,
                      latencyMs: result.latency_ms,
                    }
                  : item,
              ));
            }
            activeTurnRef.current = {
              subtitleId,
              source: mergedSource,
              sourceLanguage: result.source_language,
            };
            if (outcome.endedByPause) activeTurnRef.current = null;

            const pendingTranslation = translationQueueRef.current.at(-1);
            const combinedTranslationSource = pendingTranslation
              ? mergeTranscript(pendingTranslation.text, result.corrected_text)
              : result.corrected_text;
            if (
              pendingTranslation?.id === subtitleId &&
              pendingTranslation.sourceLanguage === result.source_language &&
              combinedTranslationSource.length <= 512
            ) {
              pendingTranslation.text = combinedTranslationSource;
            } else {
              translationQueueRef.current.push({
                id: subtitleId,
                text: result.corrected_text,
                sourceLanguage: result.source_language,
              });
            }
            void processTranslationQueue();
            const recognitionLabel = result.recognition_mode === "accurate"
              ? "AI chính xác"
              : "AI nhanh";
            setStatus(`Đã hiện lời gốc • ${recognitionLabel} • bản dịch đang tải`);
          }
          setError("");
          if (!result.corrected_text.trim()) {
            if (outcome.endedByPause) activeTurnRef.current = null;
            setStatus("Đang nghe • chưa phát hiện lời nói");
          }
        }
      }
    } finally {
      processingRef.current = false;
      void processTranslationQueue();
    }
  }, [processTranslationQueue]);

  async function startRecording() {
    // React state updates asynchronously. This synchronous lock prevents two
    // rapid clicks from opening two microphone streams on the same machine.
    if (startingRef.current || recordingActiveRef.current || captureRuntimesRef.current.size > 0) {
      return;
    }
    startingRef.current = true;
    setError("");
    setStarting(true);
    setMicPermissionPrompt(true);
    setSessionState("starting");
    const acquiredStreams: MediaStream[] = [];
    try {
      segmentStateRef.current.clear();
      packetBufferRef.current.clear();
      expectedChunkIdRef.current = 1;
      activeTurnRef.current = null;
      streamingModeRef.current = false;
      setClassroomJoinCode("");
      recordingActiveRef.current = true;
      sessionIdRef.current += 1;
      sessionStartTimeRef.current = Date.now();
      setSessionDuration(0);

      const captures: Array<{ stream: MediaStream; key: string; isTab: boolean }> = [];
      if (audioSource === "tab") {
        const stream = await navigator.mediaDevices.getDisplayMedia({ video: true, audio: true });
        acquiredStreams.push(stream);
        captures.push({ stream, key: "tab", isTab: true });
      } else {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            ...(selectedMicrophoneId
              ? { deviceId: { exact: selectedMicrophoneId } }
              : {}),
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            channelCount: 1,
            sampleRate: { ideal: 48000 },
          },
        });
        acquiredStreams.push(stream);
        void refreshMicrophones().catch(() => undefined);
        if (stream.getAudioTracks().length !== 1) {
          throw new Error("Mỗi máy chỉ được sử dụng một microphone");
        }
        captures.push({ stream, key: "microphone", isTab: false });
      }

      // WebSocket is the primary live path. REST remains available only as a
      // fallback when the socket cannot be established or later disconnects.
      try {
        const startForm = new FormData();
        startForm.append("language", translationMode);
        const res = await fetch("/api/stream/start", { method: "POST", body: startForm });
        if (!res.ok) throw new Error("Không thể khởi tạo phiên streaming");

        const streamMeta = (await res.json()) as StreamMetadata;
        if (streamMeta.join_code) setClassroomJoinCode(streamMeta.join_code);
        const ws = new WebSocket(buildAiWebSocketUrl(
          streamMeta.ws_url || `/ws/stream/${streamMeta.session_id}`,
        ));
        await new Promise<void>((resolve, reject) => {
          const timeout = window.setTimeout(() => {
            ws.close();
            reject(new Error("WebSocket streaming kết nối quá thời gian"));
          }, STREAM_CONNECT_TIMEOUT_MS);
          ws.addEventListener("open", () => {
            window.clearTimeout(timeout);
            resolve();
          }, { once: true });
          ws.addEventListener("error", () => {
            window.clearTimeout(timeout);
            reject(new Error("Không thể kết nối WebSocket streaming"));
          }, { once: true });
        });

        ws.onmessage = handleWsMessage;
        ws.onclose = () => {
          if (wsRef.current === ws) wsRef.current = null;
          if (wsPingTimerRef.current !== null) {
            window.clearInterval(wsPingTimerRef.current);
            wsPingTimerRef.current = null;
          }
          streamingModeRef.current = false;
          if (recordingActiveRef.current) {
            setStatus("Streaming bị ngắt • đã chuyển sang REST dự phòng");
          }
        };
        wsRef.current = ws;
        // IMPORTANT: Do NOT set streamingModeRef=true here.
        // Streaming mode is only activated after AudioWorklet confirms it can
        // deliver PCM data.  If AudioWorklet fails to load, the REST fallback
        // via MediaRecorder must remain active.
        wsPingTimerRef.current = window.setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ action: "ping" }));
          }
        }, STREAM_PING_INTERVAL_MS);
      } catch (err) {
        console.warn("Could not start WS streaming session, will fallback to REST mode", err);
        streamingModeRef.current = false;
      }

      for (const capture of captures) {
        if (capture.stream.getAudioTracks().length === 0) {
          throw new Error("Nguồn đã chọn không có âm thanh");
        }
        startCapture(capture.stream, capture.key, capture.isTab);
      }
      setRecording(true);
      setSessionState("recording");
      setMicPermissionPrompt(false);
      setStatus(
        `${audioSource === "tab" ? "Đang nghe âm thanh từ tab" : "Đang nghe micro"} • ${
          streamingModeRef.current ? "WebSocket streaming PCM đang bật" : "REST dự phòng đang bật"
        }`,
      );
    } catch (cause) {
      recordingActiveRef.current = false;
      stopAllCaptures();
      acquiredStreams.forEach((stream) => stream.getTracks().forEach((track) => track.stop()));
      setMicPermissionPrompt(false);
      setSessionState("idle");
      const detail = cause instanceof Error ? cause.message : "";
      setError(detail === "Nguồn đã chọn không có âm thanh" ||
        detail === "Mỗi máy chỉ được sử dụng một microphone" ||
        detail === "Mỗi máy chỉ được sử dụng một nguồn âm thanh"
        ? detail
        : audioSource === "tab"
          ? "Hãy chọn tab có âm thanh và bật Chia sẻ âm thanh."
          : "Vui lòng cấp quyền microphone để bắt đầu phiên dịch.");
      setStatus(audioSource === "tab" ? "Chưa nhận được âm thanh từ tab" : "Chưa có quyền microphone");
    } finally {
      startingRef.current = false;
      setStarting(false);
    }
  }

  function pauseRecording() {
    recordingActiveRef.current = false;
    setSessionState("paused");
    setStatus("Đã tạm dừng phiên dịch");
  }

  function resumeRecording() {
    recordingActiveRef.current = true;
    setSessionState("recording");
    setStatus("Đã tiếp tục thu âm & phiên dịch bài giảng");
  }

  async function endAndSaveSession() {
    recordingActiveRef.current = false;
    setSessionState("ended");
    setStatus("Đang chốt lời gốc và hoàn tất các bản dịch cuối…");
    const streamTail = stopAllCaptures();
    transcribeAbortRef.current.forEach((controller) => controller.abort());
    transcribeAbortRef.current.clear();
    setRecording(false);
    await streamTail;
    await new Promise<void>((resolve) => window.requestAnimationFrame(() => resolve()));
    setStatus("Phiên dịch đã kết thúc • Đã lưu bài giảng");

    if (subtitlesRef.current.length > 0) {
      const finishedSession: LectureSession = {
        id: crypto.randomUUID(),
        title: `Bài giảng ngày ${new Date().toLocaleDateString("vi-VN")} lúc ${clock(new Date().toISOString())}`,
        createdAt: new Date(sessionStartTimeRef.current || Date.now()).toISOString(),
        endedAt: new Date().toISOString(),
        durationSeconds: sessionDuration,
        subtitles: [...subtitlesRef.current],
        translationMode,
      };
      setLectureHistory((prev) => {
        const next = [finishedSession, ...prev];
        if (typeof window !== "undefined") {
          localStorage.setItem("classbridge_lecture_history", JSON.stringify(next));
        }
        return next;
      });
      localStorage.removeItem(LIVE_DRAFT_STORAGE_KEY);
    }
  }

  function exportTranscript(session: { title: string; subtitles: Subtitle[]; createdAt: string }, format: "txt" | "md" | "json") {
    let content = "";
    let mimeType = "text/plain";
    let extension = "txt";

    if (format === "txt") {
      content = `CLASSBRIDGE - PHỤ ĐỀ BÀI GIẢNG SONG NGỮ\n`;
      content += `Tiêu đề: ${session.title}\n`;
      content += `Thời gian: ${new Date(session.createdAt).toLocaleString("vi-VN")}\n`;
      content += `--------------------------------------------------------\n\n`;
      session.subtitles.forEach((s, idx) => {
        content += `[${idx + 1}] ${clock(s.createdAt)} | Lời gốc:\n`;
        content += `Gốc (${s.sourceLanguage.toUpperCase()}): ${s.source}\n`;
        content += `Dịch: ${s.translated || "(Đang dịch)"}\n\n`;
      });
    } else if (format === "md") {
      mimeType = "text/markdown";
      extension = "md";
      content = `# ${session.title}\n\n`;
      content += `> **Thời gian:** ${new Date(session.createdAt).toLocaleString("vi-VN")}\n\n`;
      content += `| STT | Thời gian | Tiếng gốc | Bản dịch |\n`;
      content += `| --- | --- | --- | --- |\n`;
      session.subtitles.forEach((s, idx) => {
        content += `| ${idx + 1} | ${clock(s.createdAt)} | ${s.source.replace(/\|/g, "\\|")} | ${(s.translated || "").replace(/\|/g, "\\|")} |\n`;
      });
    } else if (format === "json") {
      mimeType = "application/json";
      extension = "json";
      content = JSON.stringify(session, null, 2);
    }

    const blob = new Blob([content], { type: `${mimeType};charset=utf-8;` });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `classbridge_lecture_${new Date().toISOString().slice(0, 10)}_${Date.now()}.${extension}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  function deleteHistorySession(id: string) {
    setLectureHistory((prev) => {
      const next = prev.filter((s) => s.id !== id);
      if (typeof window !== "undefined") {
        localStorage.setItem("classbridge_lecture_history", JSON.stringify(next));
      }
      return next;
    });
    if (selectedHistorySession?.id === id) {
      setSelectedHistorySession(null);
    }
  }

  function startCapture(stream: MediaStream, key: string, isTabAudio: boolean) {
    if (captureRuntimesRef.current.size > 0) {
      stream.getTracks().forEach((track) => track.stop());
      throw new Error("Mỗi máy chỉ được sử dụng một nguồn âm thanh");
    }
    if (!isTabAudio && (key !== "microphone" || stream.getAudioTracks().length !== 1)) {
      stream.getTracks().forEach((track) => track.stop());
      throw new Error("Mỗi máy chỉ được sử dụng một microphone");
    }
    const audioContext = new AudioContext();
    const source = audioContext.createMediaStreamSource(stream);
    const analyser = audioContext.createAnalyser();
    analyser.fftSize = 2048;
    analyser.smoothingTimeConstant = 0.35;
    const destination = audioContext.createMediaStreamDestination();
    source.connect(analyser);
    source.connect(destination);

    // AudioWorklet delivers raw PCM float32 at 16kHz to the backend via
    // WebSocket.  Streaming mode is ONLY activated once the worklet
    // confirms it is processing audio.  Until then, REST fallback via
    // MediaRecorder remains active so no audio is silently lost.
    let pcmWorkletReady = false;
    audioContext.audioWorklet.addModule("/pcm-processor.js").then(() => {
      if (!captureRuntimesRef.current.has(key)) return;
      const pcmNode = new AudioWorkletNode(audioContext, "pcm-processor");
      source.connect(pcmNode);
      pcmNode.port.onmessage = (event) => {
        if (
          recordingActiveRef.current &&
          event.data?.type === "pcm_data" &&
          wsRef.current?.readyState === WebSocket.OPEN
        ) {
          wsRef.current.send(event.data.buffer);
          if (!pcmWorkletReady) {
            pcmWorkletReady = true;
            streamingModeRef.current = true;
            console.log("[ClassBridge] AudioWorklet PCM streaming activated");
          }
        }
      };
    }).catch((err) => {
      console.error("[ClassBridge] AudioWorklet failed to load – REST fallback active:", err);
      // pcmWorkletReady stays false → streamingModeRef stays false → REST
      // fallback via MediaRecorder continues to work.
    });

    const runtime: CaptureRuntime = {
      stream,
      audioContext,
      recorder: null,
      meterTimer: null,
      segmentTimer: null,
      audioKind: "quiet",
    };
    captureRuntimesRef.current.set(key, runtime);
    const samples = new Float32Array(analyser.fftSize);
    let chunkHasSpeech = false;
    let speechDuration = 0;
    let silenceDuration = 0;
    let noiseFloor = 0.0015;
    let segmentEndedByPause = false;
    let nextSegmentStartsNewTurn = true;
    let segmentStartedAt = 0;

    const updateCombinedAudioKind = (nextKind: AudioKind) => {
      runtime.audioKind = nextKind;
      const kinds = [...captureRuntimesRef.current.values()].map((item) => item.audioKind);
      const combined: AudioKind = kinds.includes("speech")
        ? "speech"
        : kinds.includes("background") ? "background" : "quiet";
      if (combined !== audioKindRef.current) {
        audioKindRef.current = combined;
        setAudioKind(combined);
      }
    };

    const mimeType = pickMimeType();
    const recorderOptions = mimeType
      ? { mimeType, audioBitsPerSecond: 96000 }
      : { audioBitsPerSecond: 96000 };
    const scheduleRecorderStop = (recorder: MediaRecorder, delayMs: number) => {
      if (runtime.segmentTimer !== null) window.clearTimeout(runtime.segmentTimer);
      runtime.segmentTimer = window.setTimeout(() => {
        runtime.segmentTimer = null;
        if (runtime.recorder === recorder && recorder.state === "recording") {
          segmentEndedByPause = false;
          recorder.stop();
        }
      }, delayMs);
    };
    const recordSegment = () => {
      if (!recordingActiveRef.current || !captureRuntimesRef.current.has(key)) return;
      const startsNewTurn = nextSegmentStartsNewTurn;
      nextSegmentStartsNewTurn = false;
      chunkHasSpeech = isTabAudio;
      speechDuration = isTabAudio ? AUDIO_METER_INTERVAL_MS : 0;
      silenceDuration = 0;
      segmentEndedByPause = false;
      segmentStartedAt = performance.now();
      const recorder = new MediaRecorder(destination.stream, recorderOptions);
      runtime.recorder = recorder;
      recorder.ondataavailable = (event) => {
        if (
          recordingActiveRef.current &&
          !streamingModeRef.current &&
          event.data.size > 0 &&
          chunkHasSpeech
        ) {
          queueRef.current.push({
            blob: event.data,
            endedByPause: segmentEndedByPause,
            startsNewTurn,
          });
          void processQueue();
        }
      };
      recorder.onstop = () => {
        if (recordingActiveRef.current && captureRuntimesRef.current.has(key)) {
          nextSegmentStartsNewTurn = segmentEndedByPause;
          recordSegment();
        }
      };
      recorder.onerror = () => {
        setError("Micro đã ngừng hoạt động.");
        stopRecording();
      };
      recorder.start();
      scheduleRecorderStop(
        recorder,
        isTabAudio ? MAX_PLAYBACK_UTTERANCE_MS : MAX_HYBRID_UTTERANCE_MS,
      );
    };

    runtime.meterTimer = window.setInterval(() => {
      analyser.getFloatTimeDomainData(samples);
      const rms = Math.sqrt(samples.reduce((sum, sample) => sum + sample * sample, 0) / samples.length);
      const speechThreshold = isTabAudio
        ? 0.0004
        : Math.max(0.0008, Math.min(0.003, noiseFloor * 1.2));
      const backgroundThreshold = isTabAudio
        ? 0.0002
        : Math.max(0.0005, Math.min(0.002, noiseFloor * 1.05));
      if (!isTabAudio && rms < backgroundThreshold) noiseFloor = noiseFloor * 0.95 + rms * 0.05;
      const nextKind: AudioKind = rms >= speechThreshold
        ? "speech" : rms >= backgroundThreshold ? "background" : "quiet";
      updateCombinedAudioKind(nextKind);
      speechDuration = nextKind === "speech"
        ? speechDuration + AUDIO_METER_INTERVAL_MS
        : Math.max(0, speechDuration - AUDIO_METER_INTERVAL_MS * 1.5);
      if (speechDuration >= AUDIO_METER_INTERVAL_MS && !chunkHasSpeech) {
        chunkHasSpeech = true;
        segmentStartedAt = performance.now();
        if (runtime.recorder?.state === "recording") {
          scheduleRecorderStop(
            runtime.recorder,
            isTabAudio ? MAX_PLAYBACK_UTTERANCE_MS : MAX_HYBRID_UTTERANCE_MS,
          );
        }
        silenceDuration = 0;
      } else if (speechDuration >= AUDIO_METER_INTERVAL_MS) {
        silenceDuration = 0;
      } else if (chunkHasSpeech) {
        silenceDuration += AUDIO_METER_INTERVAL_MS;
      }
      if (
        runtime.recorder?.state === "recording" && chunkHasSpeech &&
        performance.now() - segmentStartedAt >= MIN_UTTERANCE_MS &&
        silenceDuration >= AUTO_LINE_BREAK_SILENCE_MS
      ) {
        if (runtime.segmentTimer !== null) window.clearTimeout(runtime.segmentTimer);
        runtime.segmentTimer = null;
        segmentEndedByPause = true;
        runtime.recorder.stop();
      }
    }, AUDIO_METER_INTERVAL_MS);

    stream.getTracks().forEach((track) => track.addEventListener("ended", () => {
      if (recordingActiveRef.current) stopRecording();
    }, { once: true }));
    recordSegment();
  }

  function stopAllCaptures(gracefulStreamEnd = true): Promise<void> {
    let streamTail = Promise.resolve();
    if (wsPingTimerRef.current !== null) {
      window.clearInterval(wsPingTimerRef.current);
      wsPingTimerRef.current = null;
    }
    const ws = wsRef.current;
    wsRef.current = null;
    streamingModeRef.current = false;
    if (ws) {
      if (gracefulStreamEnd && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "end" }));
        streamTail = new Promise<void>((resolve) => {
          let settled = false;
          const finish = () => {
            if (settled) return;
            settled = true;
            window.clearTimeout(forceCloseTimer);
            resolve();
          };
          const forceCloseTimer = window.setTimeout(() => {
            ws.close();
            finish();
          }, 5_500);
          ws.addEventListener("message", (event) => {
            try {
              const message = JSON.parse(String(event.data));
              if (message.type === "session_end") {
                finish();
                ws.close();
              }
            } catch {
              // Ignore non-JSON messages while waiting for the graceful tail.
            }
          });
          ws.addEventListener("close", finish, { once: true });
        });
      } else {
        ws.close();
      }
    }
    for (const runtime of captureRuntimesRef.current.values()) {
      if (runtime.segmentTimer !== null) window.clearTimeout(runtime.segmentTimer);
      if (runtime.meterTimer !== null) window.clearInterval(runtime.meterTimer);
      if (runtime.recorder?.state === "recording") runtime.recorder.stop();
      runtime.stream.getTracks().forEach((track) => track.stop());
      void runtime.audioContext.close();
    }
    captureRuntimesRef.current.clear();
    return streamTail;
  }

  function selectAudioSource(nextSource: AudioSource) {
    setAudioSource(nextSource);
  }

  function stopRecording() {
    recordingActiveRef.current = false;
    sessionIdRef.current += 1;
    queueRef.current = [];
    transcribeAbortRef.current.forEach((controller) => controller.abort());
    transcribeAbortRef.current.clear();
    stopAllCaptures();
    activeTurnRef.current = null;
    audioKindRef.current = "quiet";
    setAudioKind("quiet");
    setRecording(false);
    setSessionState("paused");
    setStatus("Đã tạm dừng");
  }

  useEffect(() => {
    const transcribeControllers = transcribeAbortRef.current;
    return () => {
      recordingActiveRef.current = false;
      stopAllCaptures(false);
      sessionIdRef.current += 1;
      transcribeControllers.forEach((controller) => controller.abort());
      transcribeControllers.clear();
      translationAbortRef.current?.abort();
      queueRef.current = [];
      translationQueueRef.current = [];
    };
  }, []);

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#" aria-label="ClassBridge home">
          <span className="brand-mark">CB</span>
          <span>
            <strong>ClassBridge</strong>
            <small>AI Teacher Assistant</small>
          </span>
        </a>
        <div className="session-state">
          {sessionState === "recording" && <span className="timer-badge">⏱ {formatDuration(sessionDuration)}</span>}
          {subtitles.length > 0 && (
            <button className="topbar-btn" onClick={() => exportTranscript({ title: `Bài giảng ${new Date().toLocaleDateString("vi-VN")}`, subtitles, createdAt: new Date().toISOString() }, "txt")}>
              📥 Xuất bài giảng
            </button>
          )}
          <button className="topbar-btn" onClick={() => setShowHistoryModal(true)}>
            📜 Lịch sử ({lectureHistory.length})
          </button>
          <span className={recording ? "live-dot active" : "live-dot"} />
          {sessionState === "recording" ? "LIVE SESSION" : sessionState === "paused" ? "PAUSED" : "OFFLINE"}
        </div>
      </header>

      {micPermissionPrompt && (
        <div className="mic-permission-banner" role="alert">
          <span>🎙️</span>
          <div>
            <strong>Đang yêu cầu quyền Micro</strong>
            <p>Vui lòng chọn <strong>Cho phép (Allow)</strong> trên thông báo trình duyệt để bắt đầu thu âm bài giảng.</p>
          </div>
        </div>
      )}

      <section className="hero">
        <p className="eyebrow">FOREIGN LANGUAGE CLASSROOM • DTU</p>
        <h1>Hiểu bài giảng<br />ngay khi giảng viên nói.</h1>
        <p className="hero-copy">
          Phụ đề song ngữ Anh–Việt theo thời gian thực, được hiệu chỉnh theo
          ngữ cảnh và thuật ngữ chuyên ngành.
        </p>
      </section>

      <section className="workspace" aria-label="Live transcription workspace">
        <div className="control-card">
          <div className="section-heading">
            <span>01</span>
            <div>
              <h2>Nguồn âm thanh</h2>
              <p>Tự nhận diện tiếng Anh hoặc tiếng Việt</p>
            </div>
          </div>

          <div className="source-switch" role="group" aria-label="Loại nguồn âm thanh">
            <button
              className={audioSource === "microphone" ? "selected" : ""}
              onClick={() => selectAudioSource("microphone")}
              disabled={recording}
            >
              Micro tự động
            </button>
            <button
              className={audioSource === "tab" ? "selected" : ""}
              onClick={() => selectAudioSource("tab")}
              disabled={recording}
            >
              Tab / nhạc
            </button>
          </div>

          {audioSource === "microphone" && (
            <div className="microphone-picker">
              <label htmlFor="microphone-device">Microphone đang dùng</label>
              <div className="microphone-picker-row">
                <select
                  id="microphone-device"
                  value={selectedMicrophoneId}
                  onChange={(event) => setSelectedMicrophoneId(event.target.value)}
                  disabled={recording || starting}
                >
                  {microphones.length === 0 && <option value="">Micro mặc định</option>}
                  {microphones.map((microphone) => (
                    <option key={microphone.deviceId} value={microphone.deviceId}>
                      {microphone.label}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  onClick={() => void refreshMicrophones()}
                  disabled={recording || starting}
                >
                  Làm mới
                </button>
              </div>
              <small>Mỗi phiên chỉ dùng một micro. Kết thúc phiên để đổi sang micro khác.</small>
            </div>
          )}

          <div className="language-auto" aria-label="Lựa chọn chế độ ngôn ngữ">
            <span>AI</span>
            <div style={{ display: "flex", flexDirection: "column", gap: "6px", width: "100%" }}>
              <div style={{ display: "flex", gap: "8px" }}>
                <button
                  type="button"
                  onClick={() => setTranslationMode("vi")}
                  disabled={recording || starting}
                  style={{
                    padding: "4px 10px",
                    borderRadius: "6px",
                    border: "1px solid",
                    borderColor: translationMode === "vi" ? "#22c55e" : "#e2e8f0",
                    background: translationMode === "vi" ? "#f0fdf4" : "#ffffff",
                    color: translationMode === "vi" ? "#15803d" : "#475569",
                    fontWeight: translationMode === "vi" ? "600" : "normal",
                    cursor: "pointer",
                  }}
                >
                  🇻🇳 Tiếng Việt
                </button>
                <button
                  type="button"
                  onClick={() => setTranslationMode("en")}
                  disabled={recording || starting}
                  style={{
                    padding: "4px 10px",
                    borderRadius: "6px",
                    border: "1px solid",
                    borderColor: translationMode === "en" ? "#3b82f6" : "#e2e8f0",
                    background: translationMode === "en" ? "#eff6ff" : "#ffffff",
                    color: translationMode === "en" ? "#1d4ed8" : "#475569",
                    fontWeight: translationMode === "en" ? "600" : "normal",
                    cursor: "pointer",
                  }}
                >
                  🇬🇧 Tiếng Anh
                </button>
                <button
                  type="button"
                  onClick={() => setTranslationMode("auto")}
                  disabled={recording || starting}
                  style={{
                    padding: "4px 10px",
                    borderRadius: "6px",
                    border: "1px solid",
                    borderColor: translationMode === "auto" ? "#8b5cf6" : "#e2e8f0",
                    background: translationMode === "auto" ? "#f5f3ff" : "#ffffff",
                    color: translationMode === "auto" ? "#6d28d9" : "#475569",
                    fontWeight: translationMode === "auto" ? "600" : "normal",
                    cursor: "pointer",
                  }}
                >
                  🌐 Tự động
                </button>
              </div>
              <small>
                {translationMode === "vi"
                  ? "Khóa cứng Tiếng Việt (chuyên biệt cho giọng Hà Nội / Bắc / Trung / Nam)"
                  : translationMode === "en"
                    ? "Khóa cứng Tiếng Anh (English speech recognition)"
                    : "Tự động nhận diện và dịch thuật Anh ↔ Việt"}
              </small>
            </div>
          </div>

          {classroomJoinCode && (
            <div className="automatic-mode" aria-live="polite">
              <strong>Mã lớp trực tiếp: {classroomJoinCode}</strong>
              <small>
                Sinh viên mở đường dẫn /join/{classroomJoinCode} trên website này.
              </small>
            </div>
          )}

          <div className="mic-zone">
            <div className={recording ? "pulse-ring listening" : "pulse-ring"}>
              <button
                className="mic-button"
                onClick={recording ? (sessionState === "paused" ? resumeRecording : pauseRecording) : startRecording}
                disabled={starting}
                aria-label={recording ? "Tạm dừng phiên dịch" : "Bắt đầu phiên dịch"}
              >
                {recording ? (sessionState === "paused" ? <span className="play-icon">▶</span> : <span className="stop-icon" />) : <span className="mic-icon" />}
              </button>
            </div>
            <strong>
              {starting
                ? "Đang khởi tạo…"
                : sessionState === "recording"
                  ? `Đang thu âm (${formatDuration(sessionDuration)})`
                  : sessionState === "paused"
                    ? "Đã tạm dừng"
                    : "Bắt đầu phiên dịch"}
            </strong>
            <span>{recording
              ? "Nhấn nút micro để Tạm dừng / Tiếp tục"
              : audioSource === "tab"
                ? "Chọn tab đang phát và bật Chia sẻ âm thanh"
                : "Chọn một micro • tự nhận tiếng Anh / tiếng Việt"}</span>

            <div className="session-action-btns">
              {sessionState === "idle" || sessionState === "ended" ? (
                <button className="primary-action-btn" onClick={startRecording} disabled={starting}>
                  ▶ Bắt đầu phiên dịch
                </button>
              ) : (
                <>
                  {sessionState === "recording" ? (
                    <button className="secondary-action-btn" onClick={pauseRecording}>
                      ⏸ Tạm dừng
                    </button>
                  ) : (
                    <button className="primary-action-btn" onClick={resumeRecording}>
                      ▶ Tiếp tục phiên dịch
                    </button>
                  )}
                  <button className="danger-action-btn" onClick={endAndSaveSession}>
                    ⏹ Kết thúc & Lưu bài giảng
                  </button>
                </>
              )}
            </div>

            <div className={`audio-detection ${audioKind}`} aria-live="polite">
              <i />
              {audioKind === "speech"
                ? "Đang nhận giọng nói"
                : audioKind === "background"
                  ? "Âm thanh nền / tạp âm"
                  : "Yên lặng"}
            </div>
          </div>

          <div className="pipeline">
            <span>Một micro</span><i>→</i><span>Nhận dạng Anh / Việt</span><i>→</i><span>Dịch song song</span>
          </div>
          {error && <p className="error-message" role="alert">{error}</p>}
        </div>

        <div className="transcript-card">
          <div className="transcript-header">
            <div className="section-heading">
              <span>02</span>
              <div>
                <h2>Phụ đề trực tiếp</h2>
                <p>{status}</p>
              </div>
            </div>
            <div className="line-actions" style={{ gap: "6px" }}>
              <button
                className={`topbar-btn ${viewMode === "lines" ? "active" : ""}`}
                onClick={() => setViewMode("lines")}
                title="Hiển thị từng câu phụ đề có mốc thời gian"
              >
                📑 Từng câu
              </button>
              <button
                className={`topbar-btn ${viewMode === "document" ? "active" : ""}`}
                onClick={() => setViewMode("document")}
                title="Hiển thị đoạn văn bản"
              >
                📄 Đoạn văn
              </button>
              {subtitles.length > 0 && (
                <button
                  className="text-button"
                  onClick={() => {
                    setSubtitles([]);
                    translationQueueRef.current = [];
                    translationAbortRef.current?.abort();
                    segmentStateRef.current.clear();
                    packetBufferRef.current.clear();
                    expectedChunkIdRef.current = 1;
                    activeTurnRef.current = null;
                  }}
                >
                  Xóa tất cả
                </button>
              )}
            </div>
          </div>

          <div
            className="transcript-grid"
            aria-live="polite"
          >
            {subtitles.length === 0 ? (
              <div className="empty-state">
                <span className="sound-bars"><i /><i /><i /><i /><i /></span>
                <h3>Phụ đề sẽ xuất hiện tại đây</h3>
                <p>ClassBridge chỉ lưu văn bản. Âm thanh gốc được xóa ngay sau khi xử lý.</p>
              </div>
            ) : viewMode === "lines" ? (
              <>
                <section className="language-panel english-panel" aria-label="Lời gốc">
                    <header><span>🎤</span><div><strong>Lời gốc (Original Speech)</strong><small>Tiếng Anh / Tiếng Việt trực tiếp</small></div></header>
                    <div
                      className="language-feed"
                      ref={englishPanelRef}
                      onScroll={(e) => handlePanelScroll("en", e.currentTarget)}
                    >
                      {subtitles.map((item) => {
                        const visibleText = visibleSourceText(item);
                        if (!visibleText && !item.source && !item.unstableText) return null;
                        const hasStableUnstable = Boolean(item.isPartial && (item.stableText || item.unstableText));
                        return (
                          <article
                            className={`language-line source-line ${item.isPartial ? "live-line" : ""}`}
                            key={item.id}
                          >
                            <div className="line-header">
                              <time>{clock(item.createdAt)}</time>
                              <span className={`lang-tag lang-${item.sourceLanguage || "vi"}`}>
                                {(item.languageLabel || item.sourceLanguage || "VI").toUpperCase()}
                              </span>
                            </div>
                            <p>
                              {hasStableUnstable ? (
                                <>
                                  {item.stableText && <span className="stable-segment">{item.stableText} </span>}
                                  {item.unstableText && <span className="unstable-segment">{item.unstableText}</span>}
                                </>
                              ) : (
                                visibleText
                              )}
                              {item.isPartial && <span className="typing-caret" aria-hidden="true" />}
                            </p>
                          </article>
                        );
                      })}
                    </div>
                </section>

                <section className="language-panel vietnamese-panel" aria-label="Bản dịch">
                    <header><span>🌐</span><div><strong>Bản dịch (Translation)</strong><small>Tự động dịch sang ngôn ngữ đích</small></div></header>
                    <div
                      className="language-feed"
                      ref={vietnamesePanelRef}
                      onScroll={(e) => handlePanelScroll("vi", e.currentTarget)}
                    >
                      {subtitles.map((item) => {
                        const visibleSrc = visibleSourceText(item);
                        const transStr = (item.translated || "").trim();
                        if (!visibleSrc && !transStr) return null;
                        return (
                          <article className="language-line translated-line" key={item.id}>
                            <div className="line-header">
                              <time>{clock(item.createdAt)}</time>
                              <span className="lang-tag lang-trans">
                                Bản dịch • {item.sourceLanguage === "vi" ? "EN" : "VI"}
                              </span>
                            </div>
                            <p>
                              {transStr ? (
                                transStr
                              ) : (
                                <em className="translating">Đang dịch…</em>
                              )}
                            </p>
                          </article>
                        );
                      })}
                    </div>
                </section>
              </>
            ) : (
              <>
                <section className="language-panel english-panel" aria-label="Lời gốc">
                    <header><span>🎤</span><div><strong>Lời gốc (Original Speech)</strong><small>Văn bản dạng đoạn liên tục</small></div></header>
                    <div
                      className="language-feed"
                      ref={englishPanelRef}
                      onScroll={(e) => handlePanelScroll("en", e.currentTarget)}
                    >
                      <article className="word-document source-document">
                        <div className="document-paragraph">
                          {subtitles.map((item) => {
                            const visibleText = visibleSourceText(item);
                            if (!visibleText && !item.source && !item.unstableText) return null;
                            const hasStableUnstable = Boolean(item.isPartial && (item.stableText || item.unstableText));
                            return (
                              <span key={item.id} className={item.isPartial ? "document-segment live-segment" : "document-segment"}>
                                {hasStableUnstable ? (
                                  <>
                                    {item.stableText && <span className="stable-segment">{item.stableText} </span>}
                                    {item.unstableText && <span className="unstable-segment">{item.unstableText}</span>}
                                  </>
                                ) : (
                                  visibleText
                                )}
                                {item.isPartial && <span className="typing-caret" aria-hidden="true" />}
                                {" "}
                              </span>
                            );
                          })}
                        </div>
                      </article>
                    </div>
                </section>

                <section className="language-panel vietnamese-panel" aria-label="Bản dịch">
                    <header><span>🌐</span><div><strong>Bản dịch (Translation)</strong><small>Đoạn dịch liên tục</small></div></header>
                    <div
                      className="language-feed"
                      ref={vietnamesePanelRef}
                      onScroll={(e) => handlePanelScroll("vi", e.currentTarget)}
                    >
                      <article className="word-document translated-document">
                        <div className="document-paragraph">
                          {subtitles.map((item) => {
                            const visibleSrc = visibleSourceText(item);
                            const transStr = (item.translated || "").trim();
                            if (!visibleSrc && !transStr) return null;
                            return (
                              <span key={item.id} className="document-segment">
                                {transStr ? (
                                  transStr
                                ) : (
                                  <em className="translating">Đang dịch…</em>
                                )}
                                {" "}
                              </span>
                            );
                          })}
                        </div>
                      </article>
                    </div>
                </section>
              </>
            )}
          </div>
          {isScrolledUp && (
            <button
              className="scroll-to-bottom-btn"
              onClick={scrollToBottom}
              title="Cuộn xuống phụ đề mới nhất"
            >
              ⬇️ Cuộn xuống mới nhất
            </button>
          )}
        </div>
      </section>

      <footer>
        <span>ClassBridge MVP • Privacy-first audio processing</span>
        <span>Target latency: 1–3 seconds</span>
      </footer>

      {showHistoryModal && (
        <div className="modal-backdrop" onClick={() => setShowHistoryModal(false)}>
          <div className="modal-card" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>📜 Lịch sử các bài giảng đã lưu</h2>
              <button className="close-btn" onClick={() => setShowHistoryModal(false)}>✕</button>
            </div>
            <div className="modal-body">
              {lectureHistory.length === 0 ? (
                <p className="empty-history">Chưa có bài giảng nào được lưu. Bắt đầu một phiên dịch và nhấn &quot;Kết thúc &amp; Lưu bài giảng&quot; để xem tại đây.</p>
              ) : (
                <div className="history-list">
                  {lectureHistory.map((session) => (
                    <div key={session.id} className="history-item">
                      <div className="history-info">
                        <strong>{session.title}</strong>
                        <span>Thời lượng: {formatDuration(session.durationSeconds)} • {session.subtitles.length} câu phụ đề</span>
                        <small>{new Date(session.createdAt).toLocaleString("vi-VN")}</small>
                      </div>
                      <div className="history-actions">
                        <button onClick={() => setSelectedHistorySession(session)} title="Xem phụ đề">👁️ Xem</button>
                        <button onClick={() => exportTranscript(session, "txt")} title="Tải file .TXT">📄 .TXT</button>
                        <button onClick={() => exportTranscript(session, "md")} title="Tải file .MD">📝 .MD</button>
                        <button onClick={() => exportTranscript(session, "json")} title="Tải file .JSON">💾 .JSON</button>
                        <button className="del-btn" onClick={() => deleteHistorySession(session.id)} title="Xóa">🗑️</button>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {selectedHistorySession && (
                <div className="session-detail-view">
                  <h3>Chi tiết: {selectedHistorySession.title}</h3>
                  <div className="detail-transcript-box">
                    {selectedHistorySession.subtitles.map((sub, i) => (
                      <div key={sub.id} className="detail-line">
                        <strong>[{i + 1}] {clock(sub.createdAt)}:</strong>
                        <p className="src">Gốc ({sub.sourceLanguage.toUpperCase()}): {sub.source}</p>
                        <p className="trans">Dịch: {sub.translated || "(Đang dịch)"}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
