"use client";

import { useCallback, useEffect, useRef, useState } from "react";

// --- Types ---
type SubtitleItem = {
  id: string;
  segmentId: number;
  speakerId: number;
  source: string;
  translated: string;
  sourceLanguage: "en" | "vi";
  languageLabel: string;
  latencyMs: number;
  createdAt: string;
  isPartial?: boolean;
};

type BackendHealth = {
  status: string;
  architecture: string;
  module_1: string;
  module_2: string;
  router: string;
  translation: string;
};

function getAiBaseUrl(): string {
  if (typeof window !== "undefined") {
    const host = window.location.hostname;
    if (
      host === "localhost" ||
      host === "127.0.0.1" ||
      host === "0.0.0.0" ||
      host.startsWith("192.168.") ||
      host.startsWith("10.") ||
      host.startsWith("172.")
    ) {
      return `http://${host}:8000`;
    }
  }
  const configured = process.env.NEXT_PUBLIC_AI_SERVICE_URL?.trim();
  if (configured) return configured.replace(/\/+$/, "");
  return "http://127.0.0.1:8000";
}

function buildAiWebSocketUrl(pathWithQuery: string) {
  const base = getAiBaseUrl();
  const baseWs = base.replace(/^http/, "ws");
  const cleanPath = pathWithQuery.startsWith("/") ? pathWithQuery : `/${pathWithQuery}`;
  return `${baseWs}${cleanPath}`;
}

// --- Live Audio Waveform & VAD Visualizer (Zero React Re-render Lag) ---
function LiveAudioVisualizer({
  analyserNode,
  isRecording,
}: {
  analyserNode: AnalyserNode | null;
  isRecording: boolean;
}) {
  const barsRef = useRef<(HTMLDivElement | null)[]>([]);
  const statusRef = useRef<HTMLSpanElement | null>(null);
  const animFrameRef = useRef<number | null>(null);

  useEffect(() => {
    if (!isRecording || !analyserNode) {
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
        animFrameRef.current = null;
      }
      return;
    }

    const pcmBuffer = new Uint8Array(analyserNode.frequencyBinCount);

    const updateMeter = () => {
      analyserNode.getByteFrequencyData(pcmBuffer);
      let sum = 0;
      for (let i = 0; i < pcmBuffer.length; i++) sum += pcmBuffer[i];
      const avg = sum / pcmBuffer.length;
      const normalized = Math.min(100, Math.round((avg / 128) * 100));

      for (let bar = 1; bar <= 8; bar++) {
        const el = barsRef.current[bar - 1];
        if (el) {
          const height = Math.max(4, Math.min(24, Math.round((normalized / 100) * (bar * 3 + 8))));
          el.style.height = `${height}px`;
          if (normalized > 15) {
            el.classList.add("active");
          } else {
            el.classList.remove("active");
          }
        }
      }

      if (statusRef.current) {
        if (normalized > 18) {
          statusRef.current.innerText = "Đang nói";
          statusRef.current.className = "text-xs font-mono font-bold uppercase text-emerald-400";
        } else if (normalized > 6) {
          statusRef.current.innerText = "Lọc ồn";
          statusRef.current.className = "text-xs font-mono font-bold uppercase text-amber-400";
        } else {
          statusRef.current.innerText = "Yên lặng";
          statusRef.current.className = "text-xs font-mono font-bold uppercase text-slate-500";
        }
      }

      animFrameRef.current = requestAnimationFrame(updateMeter);
    };

    animFrameRef.current = requestAnimationFrame(updateMeter);

    return () => {
      if (animFrameRef.current) {
        cancelAnimationFrame(animFrameRef.current);
        animFrameRef.current = null;
      }
    };
  }, [isRecording, analyserNode]);

  if (!isRecording) return null;

  return (
    <div className="flex items-center gap-3 px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-800">
      <div className="visualizer-strip">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((bar, i) => (
          <div
            key={bar}
            ref={(el) => {
              barsRef.current[i] = el;
            }}
            className="wave-bar"
            style={{ height: "4px" }}
          />
        ))}
      </div>
      <span
        ref={statusRef}
        className="text-xs font-mono font-bold uppercase text-slate-500"
      >
        Yên lặng
      </span>
    </div>
  );
}

export default function AudioSpeechApp() {
  // Backend Health
  const [aiHealth, setAiHealth] = useState<BackendHealth | null>(null);
  const [isAiOnline, setIsAiOnline] = useState<boolean>(false);
  const [activeModulePill, setActiveModulePill] = useState<string>("Tự động nhận diện");

  // Audio Session State
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [sessionDuration, setSessionDuration] = useState<number>(0);
  const [specialistMode, setSpecialistMode] = useState<"auto" | "vi" | "en">("auto");
  const [translationTarget, setTranslationTarget] = useState<"auto" | "en" | "vi">("auto");
  const [audioSource, setAudioSource] = useState<"microphone" | "tab">("microphone");
  const [viewMode, setViewMode] = useState<"dual" | "single">("dual");
  const [subtitles, setSubtitles] = useState<SubtitleItem[]>([]);
  const [activeAnalyser, setActiveAnalyser] = useState<AnalyserNode | null>(null);
  const [fontSize, setFontSize] = useState<"normal" | "large" | "xlarge">("normal");
  const [autoScroll, setAutoScroll] = useState<boolean>(true);
  const [userScrolledUp, setUserScrolledUp] = useState<boolean>(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);

  // Refs for Audio & WebSocket
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<number | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const leftColRef = useRef<HTMLDivElement | null>(null);
  const rightColRef = useRef<HTMLDivElement | null>(null);
  const prevSubtitlesCountRef = useRef<number>(0);

  // 1. Health check every 10s
  const checkHealth = useCallback(async () => {
    try {
      const res = await fetch(`${getAiBaseUrl()}/health`, {
        signal: AbortSignal.timeout(3000),
      });
      if (res.ok) {
        const data = (await res.json()) as BackendHealth;
        setAiHealth(data);
        setIsAiOnline(true);
      } else {
        setIsAiOnline(false);
      }
    } catch {
      setIsAiOnline(false);
    }
  }, []);

  useEffect(() => {
    checkHealth();
    const interval = window.setInterval(checkHealth, 10000);
    return () => window.clearInterval(interval);
  }, [checkHealth]);

  // Session duration timer
  useEffect(() => {
    if (isRecording) {
      timerRef.current = window.setInterval(() => {
        setSessionDuration((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) window.clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) window.clearInterval(timerRef.current);
    };
  }, [isRecording]);

  // Smooth auto-scroll when new items arrive
  useEffect(() => {
    if (!autoScroll || userScrolledUp) {
      prevSubtitlesCountRef.current = subtitles.length;
      return;
    }

    if (subtitles.length > prevSubtitlesCountRef.current) {
      const scrollOpt: ScrollToOptions = { behavior: "smooth" };
      if (leftColRef.current) {
        leftColRef.current.scrollTo({
          top: leftColRef.current.scrollHeight,
          ...scrollOpt,
        });
      }
      if (rightColRef.current) {
        rightColRef.current.scrollTo({
          top: rightColRef.current.scrollHeight,
          ...scrollOpt,
        });
      }
    }
    prevSubtitlesCountRef.current = subtitles.length;
  }, [subtitles, autoScroll, userScrolledUp]);

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m.toString().padStart(2, "0")}:${s.toString().padStart(2, "0")}`;
  };

  const getClock = (iso: string) => {
    try {
      return new Date(iso).toLocaleTimeString("vi-VN", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
    } catch {
      return "";
    }
  };

  // --- WebSocket & Live Audio Streaming ---
  const startLiveSession = async () => {
    try {
      stopLiveSession();
      await new Promise((resolve) => setTimeout(resolve, 50));

      setSubtitles([]);
      prevSubtitlesCountRef.current = 0;
      setSessionDuration(0);

      // 1. Get audio media stream at 16kHz
      let stream: MediaStream;
      if (audioSource === "tab") {
        stream = await navigator.mediaDevices.getDisplayMedia({
          video: true,
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            sampleRate: 16000,
          },
        });
      } else {
        stream = await navigator.mediaDevices.getUserMedia({
          audio: {
            echoCancellation: true,
            noiseSuppression: true,
            autoGainControl: true,
            channelCount: 1,
            sampleRate: { ideal: 16000 },
          },
        });
      }

      mediaStreamRef.current = stream;

      // 2. Setup AudioContext at 16kHz & Analyser for VU Meter
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const audioContext = new AudioCtx({ sampleRate: 16000 });
      audioContextRef.current = audioContext;

      if (audioContext.state === "suspended") {
        await audioContext.resume();
      }

      const source = audioContext.createMediaStreamSource(stream);
      const analyser = audioContext.createAnalyser();
      analyser.fftSize = 256;
      source.connect(analyser);
      analyserRef.current = analyser;
      setActiveAnalyser(analyser);

      // 3. Request Session from Backend
      const startForm = new FormData();
      startForm.append("language", specialistMode);
      const startRes = await fetch(`${getAiBaseUrl()}/stream/start`, {
        method: "POST",
        body: startForm,
      });

      let wsUrl = `${buildAiWebSocketUrl("/ws/stream")}?lang=${specialistMode}&trans_lang=${translationTarget}`;
      if (startRes.ok) {
        const startData = (await startRes.json()) as { session_id?: string; ws_url?: string };
        if (startData.session_id) {
          wsUrl = `${buildAiWebSocketUrl(`/ws/stream/${startData.session_id}`)}?lang=${specialistMode}&trans_lang=${translationTarget}`;
        } else if (startData.ws_url) {
          wsUrl = buildAiWebSocketUrl(startData.ws_url);
        }
      }

      // 4. Connect WebSocket
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsRecording(true);
        ws.send(JSON.stringify({ action: "set_language", language: specialistMode }));
        ws.send(JSON.stringify({ action: "set_translation_target", target: translationTarget }));
      };

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data);
          if (msg.type === "pong") return;

          if (msg.type === "language_changed") {
            return;
          }

          if (msg.type === "final" || msg.type === "partial") {
            const transcript = (msg.transcript || msg.stable_text || "").trim();
            if (!transcript) return;

            const segmentId = Number(msg.segment_id) || Date.now();
            const subtitleId = `seg_${segmentId}`;
            const isFinal = msg.type === "final";
            const lang = (msg.language || "vi") as "en" | "vi";
            const langLabel = msg.language_label || (lang === "en" ? "en" : "vi");
            const translation = String(msg.translation || "").trim();

            if (langLabel === "en") {
              setActiveModulePill("Module 2 (English)");
            } else if (langLabel === "mixed_vi_en") {
              setActiveModulePill("Module 1 (Song ngữ / IT)");
            } else {
              setActiveModulePill("Module 1 (Tiếng Việt)");
            }

            setSubtitles((prev) => {
              const idx = prev.findIndex((s) => s.id === subtitleId);
              if (idx === -1) {
                // Chỉ bỏ qua nếu là gói tin trùng lặp gửi dồn dập trong khoảng 1.2s
                const lastItem = prev.length > 0 ? prev[prev.length - 1] : null;
                if (
                  lastItem &&
                  lastItem.source.trim().toLowerCase() === transcript.trim().toLowerCase() &&
                  Date.now() - new Date(lastItem.createdAt).getTime() < 1200
                ) {
                  return prev;
                }

                return [
                  ...prev,
                  {
                    id: subtitleId,
                    segmentId,
                    speakerId: msg.speaker_id || 1,
                    source: transcript,
                    translated: translation,
                    sourceLanguage: lang,
                    languageLabel: langLabel,
                    latencyMs: msg.latency_ms || 45,
                    createdAt: new Date().toISOString(),
                    isPartial: !isFinal,
                  },
                ];
              } else {
                const next = [...prev];
                next[idx] = {
                  ...next[idx],
                  source: transcript,
                  translated: translation || next[idx].translated,
                  isPartial: !isFinal,
                  sourceLanguage: lang,
                  languageLabel: langLabel,
                };
                return next;
              }
            });
          } else if (msg.type === "translation") {
            const trans = String(msg.translation || "").trim();
            const segmentId = Number(msg.segment_id);
            if (trans && segmentId) {
              setSubtitles((prev) =>
                prev.map((s) => (s.segmentId === segmentId ? { ...s, translated: trans } : s))
              );
            }
          }
        } catch (e) {
          console.error("WS message parse error:", e);
        }
      };

      ws.onerror = (err) => {
        console.error("WebSocket error:", err);
      };

      ws.onclose = () => {
        setIsRecording(false);
      };

      // 5. Load AudioWorklet for 16kHz PCM Float32 Streaming
      await audioContext.audioWorklet.addModule("/pcm-processor.js");
      const pcmNode = new AudioWorkletNode(audioContext, "pcm-processor");
      source.connect(pcmNode);

      const muteGain = audioContext.createGain();
      muteGain.gain.value = 0;
      pcmNode.connect(muteGain);
      muteGain.connect(audioContext.destination);

      pcmNode.port.onmessage = (e) => {
        if (e.data?.type === "pcm_data" && ws.readyState === WebSocket.OPEN) {
          ws.send(e.data.buffer);
        }
      };
    } catch (err) {
      console.error("Failed to start audio session:", err);
      alert("Không thể khởi động micro hoặc kết nối AI Service. Vui lòng cấp quyền micro và đảm bảo Backend port 8000 đang hoạt động.");
      stopLiveSession();
    }
  };

  const stopLiveSession = () => {
    if (wsRef.current) {
      if (wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ action: "end" }));
      }
      wsRef.current.close();
      wsRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }

    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }

    analyserRef.current = null;
    setActiveAnalyser(null);
    setIsRecording(false);
  };

  // Change language on the fly
  const handleSpecialistChange = (mode: "auto" | "vi" | "en") => {
    setSpecialistMode(mode);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "set_language", language: mode }));
    }
  };

  const handleTranslationTargetChange = (target: "auto" | "en" | "vi") => {
    setTranslationTarget(target);
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ action: "set_translation_target", target }));
    }
  };

  const copyText = (text: string, id: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  };

  const speakText = (text: string, lang: string) => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = lang === "en" ? "en-US" : "vi-VN";
      window.speechSynthesis.speak(utterance);
    }
  };

  const exportTxt = () => {
    if (subtitles.length === 0) return;
    const content = subtitles
      .map(
        (s, i) =>
          `[${i + 1}] [${s.languageLabel.toUpperCase()}] ${s.source}${
            s.translated ? `\n    -> ${s.translated}` : ""
          }`
      )
      .join("\n\n");
    const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `ClassBridge_Audio_${new Date().toISOString().slice(0, 19).replace(/:/g, "-")}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen flex flex-col">
      {/* Top Header */}
      <header className="header-glass">
        <div className="header-inner">
          <div className="brand-badge">
            <div className="brand-icon-box">🎙️</div>
            <div className="brand-titles">
              <h1>
                ClassBridge <span>Voice AI</span>
              </h1>
              <p>Hệ thống Nhận diện Âm thanh Thời gian thực (Realtime Speech-to-Text)</p>
            </div>
          </div>

          <div className="telemetry-strip">
            {/* Backend Connectivity */}
            <div className="telemetry-pill" title="FastAPI Backend Port 8000">
              <span className={`status-dot ${isAiOnline ? "online" : ""}`} />
              <span>AI Service:</span>
              <strong className={isAiOnline ? "text-emerald-400" : "text-rose-400"}>
                {isAiOnline ? "PORT 8000 OK" : "OFFLINE"}
              </strong>
            </div>

            {/* Active AI Module */}
            <div className="telemetry-pill hidden sm:flex">
              <span>Định tuyến:</span>
              <strong className="text-cyan-400">{activeModulePill}</strong>
            </div>

            {/* Session Timer */}
            {isRecording && (
              <div className="telemetry-pill border-rose-500/40 bg-rose-950/40 text-rose-300">
                <span className="status-dot recording" />
                <span>REC:</span>
                <strong className="font-mono">{formatTime(sessionDuration)}</strong>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="app-container flex-1 flex flex-col pt-6">
        {/* Audio Control Bar */}
        <div className="control-bar">
          {/* Left: Primary Action & Audio Input Settings */}
          <div className="control-group">
            {!isRecording ? (
              <button onClick={startLiveSession} className="btn-primary">
                <span className="text-lg">▶</span>
                <span>Bắt đầu Thu âm</span>
              </button>
            ) : (
              <button onClick={stopLiveSession} className="btn-danger">
                <span className="text-lg">⏹</span>
                <span>Dừng Thu âm</span>
              </button>
            )}

            {/* Audio Source */}
            <div className="segmented-control" title="Chọn nguồn âm thanh">
              <button
                disabled={isRecording}
                onClick={() => setAudioSource("microphone")}
                className={`segmented-btn ${audioSource === "microphone" ? "active" : ""}`}
              >
                🎤 Micro
              </button>
              <button
                disabled={isRecording}
                onClick={() => setAudioSource("tab")}
                className={`segmented-btn ${audioSource === "tab" ? "active" : ""}`}
              >
                🖥️ Tab Audio
              </button>
            </div>

            {/* Speech Language Mode */}
            <div className="segmented-control" title="Chọn chế độ nhận diện giọng nói">
              <button
                onClick={() => handleSpecialistChange("auto")}
                className={`segmented-btn ${specialistMode === "auto" ? "active" : ""}`}
                title="Tự động nhận diện song ngữ Anh - Việt"
              >
                ⚡ Tự động
              </button>
              <button
                onClick={() => handleSpecialistChange("vi")}
                className={`segmented-btn ${specialistMode === "vi" ? "active" : ""}`}
                title="Chỉ nhận diện Tiếng Việt"
              >
                🇻🇳 Tiếng Việt
              </button>
              <button
                onClick={() => handleSpecialistChange("en")}
                className={`segmented-btn ${specialistMode === "en" ? "active" : ""}`}
                title="Chỉ nhận diện Tiếng Anh"
              >
                🇬🇧 Tiếng Anh
              </button>
            </div>
          </div>

          {/* Right: Audio Visualizer & Display Controls */}
          <div className="control-group">
            {/* Realtime Waveform VU Meter */}
            <LiveAudioVisualizer analyserNode={activeAnalyser} isRecording={isRecording} />

            {/* View Mode: Song ngữ vs Chỉ lời gốc */}
            <div className="segmented-control" title="Chế độ hiển thị">
              <button
                onClick={() => setViewMode("dual")}
                className={`segmented-btn ${viewMode === "dual" ? "active" : ""}`}
              >
                📖 Song ngữ
              </button>
              <button
                onClick={() => setViewMode("single")}
                className={`segmented-btn ${viewMode === "single" ? "active" : ""}`}
              >
                🎙️ Chỉ lời gốc
              </button>
            </div>

            {/* Font Size Switcher */}
            <div className="segmented-control" title="Cỡ chữ">
              <button
                onClick={() => setFontSize("normal")}
                className={`segmented-btn ${fontSize === "normal" ? "active" : ""}`}
              >
                A
              </button>
              <button
                onClick={() => setFontSize("large")}
                className={`segmented-btn ${fontSize === "large" ? "active" : ""}`}
              >
                A+
              </button>
              <button
                onClick={() => setFontSize("xlarge")}
                className={`segmented-btn ${fontSize === "xlarge" ? "active" : ""}`}
              >
                A++
              </button>
            </div>

            {/* Download Text */}
            {subtitles.length > 0 && (
              <button onClick={exportTxt} className="btn-secondary" title="Tải toàn bộ phụ đề dạng .TXT">
                📄 Xuất TXT
              </button>
            )}

            {/* Clear Screen */}
            <button
              onClick={() => setSubtitles([])}
              className="btn-secondary"
              title="Xóa danh sách phụ đề trên màn hình"
            >
              🧹 Xóa
            </button>
          </div>
        </div>

        {/* Subtitles Display Feed */}
        <div className={`dual-feed-grid ${viewMode === "single" ? "single-column" : ""}`}>
          {/* Column 1: Lời nói gốc (Realtime Speech-to-Text) */}
          <div className="feed-column">
            <div className="feed-header">
              <div className="feed-title">
                <span className="text-xl">🎤</span>
                <div>
                  <h3>Lời nói gốc (Realtime Speech)</h3>
                  <p className="text-xs text-slate-400">
                    Phát biểu ra gì hiện ra đó — Whisper ASR thời gian thực
                  </p>
                </div>
              </div>
              <div className="text-xs text-slate-400 font-mono">
                {subtitles.length} câu
              </div>
            </div>

            <div
              ref={leftColRef}
              className="feed-body"
              onScroll={(e) => {
                const el = e.currentTarget;
                const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 50;
                setUserScrolledUp(!isNearBottom);
              }}
            >
              {subtitles.length === 0 ? (
                <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-500">
                  <div className="w-16 h-16 mb-4 rounded-2xl bg-slate-900 border border-slate-800 grid place-items-center text-3xl">
                    🎙️
                  </div>
                  <h4 className="text-base font-semibold text-slate-400 mb-1">
                    Sẵn sàng thu âm giọng nói
                  </h4>
                  <p className="text-xs max-w-sm leading-relaxed text-slate-400">
                    Nhấn nút <strong>&quot;Bắt đầu Thu âm&quot;</strong> và nói vào Micro. Lời nói của bạn sẽ được nhận diện và hiển thị tức thời tại đây.
                  </p>
                </div>
              ) : (
                subtitles.map((item) => (
                  <div
                    key={item.id}
                    className={`subtitle-card group ${item.isPartial ? "live-speaking" : ""}`}
                  >
                    <div className="subtitle-meta">
                      <div className="meta-left">
                        <span className="subtitle-time">{getClock(item.createdAt)}</span>
                        <span
                          className={`module-badge ${
                            item.languageLabel === "en" ? "badge-en" : "badge-vi"
                          }`}
                        >
                          {item.languageLabel === "en" ? "🇬🇧 EN" : "🇻🇳 VI"}
                        </span>
                        {item.latencyMs > 0 && (
                          <span className="text-[10px] text-slate-500 font-mono">
                            {item.latencyMs}ms
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                        <button
                          onClick={() => copyText(item.source, item.id)}
                          className="text-xs text-slate-400 hover:text-emerald-400 px-1.5 py-0.5 rounded font-mono"
                          title="Sao chép câu nói"
                        >
                          {copiedId === item.id ? "✓ Đã chép" : "📋 Chép"}
                        </button>
                      </div>
                    </div>

                    <p
                      className={`subtitle-text ${
                        fontSize === "large"
                          ? "text-lg"
                          : fontSize === "xlarge"
                          ? "text-xl font-medium"
                          : "text-base"
                      }`}
                    >
                      {item.source}
                      {item.isPartial && <span className="typing-caret" />}
                    </p>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Column 2: Bản dịch học thuật (Chỉ hiện khi viewMode === "dual") */}
          {viewMode === "dual" && (
            <div className="feed-column">
              <div className="feed-header">
                <div className="feed-title">
                  <span className="text-xl">🌐</span>
                  <div>
                    <h3>Bản dịch học thuật (Academic Translation)</h3>
                    <p className="text-xs text-slate-400">
                      Tự động dịch sang ngôn ngữ đối ứng
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <div className="segmented-control" title="Chọn chiều dịch">
                    <button
                      onClick={() => handleTranslationTargetChange("auto")}
                      className={`segmented-btn ${translationTarget === "auto" ? "active" : ""}`}
                    >
                      🔄 Tự động
                    </button>
                    <button
                      onClick={() => handleTranslationTargetChange("en")}
                      className={`segmented-btn ${translationTarget === "en" ? "active" : ""}`}
                    >
                      🇬🇧 Sang EN
                    </button>
                    <button
                      onClick={() => handleTranslationTargetChange("vi")}
                      className={`segmented-btn ${translationTarget === "vi" ? "active" : ""}`}
                    >
                      🇻🇳 Sang VI
                    </button>
                  </div>
                </div>
              </div>

              <div
                ref={rightColRef}
                className="feed-body"
                onScroll={(e) => {
                  const el = e.currentTarget;
                  const isNearBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 50;
                  setUserScrolledUp(!isNearBottom);
                }}
              >
                {subtitles.length === 0 ? (
                  <div className="h-full flex flex-col items-center justify-center text-center p-8 text-slate-500">
                    <div className="w-16 h-16 mb-4 rounded-2xl bg-slate-900 border border-slate-800 grid place-items-center text-3xl">
                      🌐
                    </div>
                    <h4 className="text-base font-semibold text-slate-400 mb-1">
                      Bản dịch sẽ hiển thị song song
                    </h4>
                    <p className="text-xs max-w-sm leading-relaxed text-slate-400">
                      Mỗi câu nói được nhận diện sẽ được dịch sang ngôn ngữ đối ứng với độ trễ thấp.
                    </p>
                  </div>
                ) : (
                  subtitles.map((item) => (
                    <div key={`trans_${item.id}`} className="subtitle-card group">
                      <div className="subtitle-meta">
                        <span className="subtitle-time">{getClock(item.createdAt)}</span>
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          {item.translated && (
                            <>
                              <button
                                onClick={() =>
                                  speakText(
                                    item.translated,
                                    item.sourceLanguage === "vi" ? "en" : "vi"
                                  )
                                }
                                className="text-xs text-slate-400 hover:text-cyan-400 p-1 rounded"
                                title="Đọc phát âm (TTS)"
                              >
                                🔊
                              </button>
                              <button
                                onClick={() => copyText(item.translated, `t_${item.id}`)}
                                className="text-xs text-slate-400 hover:text-emerald-400 px-1.5 py-0.5 rounded font-mono"
                                title="Sao chép bản dịch"
                              >
                                {copiedId === `t_${item.id}` ? "✓ Đã chép" : "📋 Chép"}
                              </button>
                            </>
                          )}
                        </div>
                      </div>

                      <p
                        className={`subtitle-text translated ${
                          fontSize === "large"
                            ? "text-lg"
                            : fontSize === "xlarge"
                            ? "text-xl font-medium"
                            : "text-base"
                        }`}
                      >
                        {item.translated ? (
                          item.translated
                        ) : (
                          <em className="text-slate-500 italic text-sm animate-pulse">
                            Đang dịch tức thời…
                          </em>
                        )}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* Scroll down button if user scrolled up */}
        {userScrolledUp && (
          <div className="flex justify-center mt-3">
            <button
              onClick={() => {
                setUserScrolledUp(false);
                if (leftColRef.current) {
                  leftColRef.current.scrollTo({
                    top: leftColRef.current.scrollHeight,
                    behavior: "smooth",
                  });
                }
                if (rightColRef.current) {
                  rightColRef.current.scrollTo({
                    top: rightColRef.current.scrollHeight,
                    behavior: "smooth",
                  });
                }
              }}
              className="btn-secondary shadow-lg bg-emerald-950/80 border-emerald-500/50 text-emerald-300"
            >
              ⬇️ Cuộn xuống câu mới nhất
            </button>
          </div>
        )}
      </main>
    </div>
  );
}
