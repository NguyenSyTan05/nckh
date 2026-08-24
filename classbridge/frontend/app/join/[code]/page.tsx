"use client";

import { useEffect, useRef, useState } from "react";
import { useParams } from "next/navigation";
import { cleanRepetitions } from "../../utils/textUtils";

type Subtitle = {
  id: string;
  speakerId: number;
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

type ClassroomHistoryItem = {
  segment_id?: string;
  speaker_id?: number;
  transcript?: string;
  translation?: string;
  language?: "en" | "vi";
  language_label?: "en" | "vi" | "mixed";
  latency_ms?: number;
};

type ClassroomMessage = ClassroomHistoryItem & {
  type?: "init_history" | "partial" | "final" | "translation" | "session_end" | "pong";
  stable_text?: string;
  unstable_text?: string;
  history?: ClassroomHistoryItem[];
};

function buildAiWebSocketUrl(pathname: string) {
  const configuredBase = process.env.NEXT_PUBLIC_AI_SERVICE_URL?.trim();
  const url = configuredBase
    ? new URL(configuredBase, window.location.href)
    : new URL(window.location.href);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  if (!configuredBase) url.port = "8000";
  url.pathname = pathname.startsWith("/") ? pathname : `/${pathname}`;
  url.search = "";
  url.hash = "";
  return url.toString();
}

export default function StudentClassroomView() {
  const params = useParams();
  const joinCode = String(params?.code || "").toUpperCase();

  const [connected, setConnected] = useState(false);
  const [error, setError] = useState("");
  const [subtitles, setSubtitles] = useState<Subtitle[]>([]);
  const [status, setStatus] = useState("Đang kết nối vào lớp học...");
  const activeTurnIdRef = useRef<string | null>(null);

  const englishPanelRef = useRef<HTMLDivElement | null>(null);
  const vietnamesePanelRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    for (const panel of [englishPanelRef.current, vietnamesePanelRef.current]) {
      if (panel) panel.scrollTop = panel.scrollHeight;
    }
  }, [subtitles]);

  useEffect(() => {
    if (!joinCode) return;

    let ws: WebSocket | null = null;
    let disposed = false;
    const controller = new AbortController();

    async function initStudentConnection() {
      try {
        const res = await fetch(
          `/api/stream/start?join_code=${encodeURIComponent(joinCode)}`,
          { signal: controller.signal },
        );
        if (!res.ok) {
          const data = (await res.json()) as { detail?: string; error?: string };
          setError(data.detail || data.error || "Không tìm thấy lớp học.");
          setStatus("Mã lớp không hợp lệ");
          return;
        }

        const data = (await res.json()) as {
          join_code: string;
          language: string;
          history?: ClassroomHistoryItem[];
          ws_url?: string;
        };
        if (disposed) return;
        setStatus(`Đang kết nối vào lớp ${data.join_code}…`);

        ws = new WebSocket(buildAiWebSocketUrl(
          data.ws_url || `/ws/classroom/${data.join_code}`,
        ));
        ws.onopen = () => {
          setConnected(true);
          setStatus(`Đã tham gia lớp ${data.join_code} • Đang nghe giảng trực tiếp`);
        };

        const segmentStateMap = new Map<number, { lastRevision: number; finalCommitted: boolean }>();

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(String(event.data));
            if (msg.type === "init_history") {
              const historyItems: Subtitle[] = (msg.history || []).map((h: any, idx: number) => {
                const segId = Number(h.segment_id) || idx + 1;
                segmentStateMap.set(segId, { lastRevision: Number(h.revision) || 1, finalCommitted: true });
                return {
                  id: `seg_${segId}`,
                  speakerId: h.speaker_id || 1,
                  source: h.text || h.transcript || "",
                  translated: h.translation || "",
                  sourceLanguage: h.language || "vi",
                  languageLabel: h.language_label || h.language || "vi",
                  latencyMs: h.latency_ms || 0,
                  createdAt: new Date().toISOString(),
                };
              });
              setSubtitles(historyItems);
            } else if (msg.type === "partial" || msg.type === "final") {
              const segmentId = Number(msg.segment_id) || 0;
              const revision = Number(msg.revision) || 0;
              const isFinal = Boolean(msg.final || msg.type === "final");
              const speakerId = Math.max(1, msg.speaker_id || 1);
              const rawTranscript = msg.text || msg.transcript || "";
              const transcript = cleanRepetitions(rawTranscript);
              const sourceLanguage: "en" | "vi" = msg.language === "en" ? "en" : "vi";

              if (!segmentId) return;
              if (!transcript.trim() && !isFinal) return;

              const prior = segmentStateMap.get(segmentId) ?? { lastRevision: 0, finalCommitted: false };
              if (prior.finalCommitted && !isFinal) return;
              if (revision <= prior.lastRevision && !isFinal) return;

              prior.lastRevision = Math.max(prior.lastRevision, revision);
              if (isFinal) prior.finalCommitted = true;
              segmentStateMap.set(segmentId, prior);

              const subtitleId = `seg_${segmentId}`;

              setSubtitles((prev) => {
                const index = prev.findIndex((item) => item.id === subtitleId);
                if (index === -1) {
                  if (!transcript.trim()) return prev;
                  return [
                    ...prev,
                    {
                      id: subtitleId,
                      speakerId,
                      source: transcript,
                      stableText: isFinal ? transcript : cleanRepetitions(msg.stable_text || ""),
                      unstableText: isFinal ? "" : msg.unstable_text,
                      isPartial: !isFinal,
                      translated: isFinal && msg.translation ? cleanRepetitions(msg.translation) : "",
                      sourceLanguage,
                      languageLabel: msg.language_label || sourceLanguage,
                      latencyMs: msg.latency_ms || 0,
                      createdAt: new Date().toISOString(),
                    },
                  ];
                }

                const existing = prev[index];
                if (existing.isPartial === false && !isFinal) return prev;

                const next = [...prev];
                const nextSource = transcript || existing.source;
                if (!nextSource.trim()) {
                  return prev;
                }

                next[index] = {
                  ...existing,
                  source: nextSource,
                  stableText: isFinal ? nextSource : cleanRepetitions(msg.stable_text || ""),
                  unstableText: isFinal ? "" : (msg.unstable_text || ""),
                  isPartial: !isFinal,
                  translated: msg.translation ? cleanRepetitions(msg.translation) : existing.translated,
                  sourceLanguage,
                  languageLabel: msg.language_label || sourceLanguage,
                };
                return next;
              });
            } else if (msg.type === "translation" && msg.segment_id) {
              const segId = Number(msg.segment_id);
              const subId = `seg_${segId}`;
              setSubtitles((prev) => prev.map((item) =>
                item.id === subId || item.id === String(msg.segment_id)
                  ? { ...item, translated: msg.translation || "" }
                  : item,
              ));
            } else if (msg.type === "session_end") {
              setStatus("Bài giảng đã kết thúc • phụ đề cuối đã hoàn tất");
              ws?.close();
            }
          } catch (err) {
            console.error("Student WS parse error", err);
          }
        };

        ws.onclose = () => {
          setConnected(false);
          setStatus((current) => current.includes("đã kết thúc")
            ? current
            : "Đã ngắt kết nối khỏi lớp học.");
        };
        ws.onerror = () => setError("Không thể mở kết nối phụ đề trực tiếp.");
      } catch (err) {
        if (err instanceof DOMException && err.name === "AbortError") return;
        setError("Không thể kết nối tới server AI.");
        setStatus("Lỗi kết nối");
      }
    }

    void initStudentConnection();

    return () => {
      disposed = true;
      controller.abort();
      if (ws) ws.close();
    };
  }, [joinCode]);

  function clock(iso: string) {
    return new Intl.DateTimeFormat("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    }).format(new Date(iso));
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#">
          <span className="brand-mark">CB</span>
          <span>
            <strong>ClassBridge Student View</strong>
            <small>Phòng học: {joinCode}</small>
          </span>
        </a>
        <div className="session-state">
          <span className={connected ? "live-dot active" : "live-dot"} />
          {connected ? "STUDENT LIVE MODE" : "DISCONNECTED"}
        </div>
      </header>

      <section className="hero" style={{ padding: "30px 0 20px" }}>
        <p className="eyebrow">CLASSROOM JOIN CODE: {joinCode}</p>
        <h1 style={{ fontSize: "36px" }}>Phụ đề bài giảng trực tiếp</h1>
        <p className="hero-copy" style={{ fontSize: "15px" }}>
          Màn hình phụ đề dành cho sinh viên. Tự động hiển thị lời giảng và bản dịch song ngữ thời gian thực.
        </p>
      </section>

      {error ? (
        <div className="error-message" style={{ fontSize: "16px", padding: "20px" }}>
          ❌ {error}
        </div>
      ) : (
        <div className="transcript-card" style={{ minHeight: "550px" }}>
          <div className="transcript-header">
            <div className="section-heading">
              <span>LIVE</span>
              <div>
                <h2>{status}</h2>
                <p>Chế độ đọc dành cho Sinh viên (Read-Only)</p>
              </div>
            </div>
          </div>

          <div className="transcript-grid" aria-live="polite">
            {subtitles.length === 0 ? (
              <div className="empty-state">
                <span className="sound-bars"><i /><i /><i /><i /><i /></span>
                <h3>Đang chờ giảng viên phát biểu...</h3>
                <p>Phụ đề và bản dịch sẽ hiển thị tự động tại đây ngay khi thầy cô bắt đầu giảng bài.</p>
              </div>
            ) : (
              <>
                <section className="language-panel english-panel" aria-label="Lời gốc">
                  <header><span>🎤</span><div><strong>Lời gốc</strong><small>EN / VI / Mixed tự động</small></div></header>
                  <div className="language-feed" ref={englishPanelRef}>
                    {subtitles.map((item) => {
                      const hasStableUnstable = Boolean(item.isPartial && (item.stableText || item.unstableText));
                      return (
                        <article className="language-line source-line" key={item.id}>
                          <div><time>{clock(item.createdAt)}</time><span>Người {item.speakerId} • {(item.languageLabel || item.sourceLanguage).toUpperCase()}</span></div>
                          <p>
                            {hasStableUnstable ? (
                              <>
                                {item.stableText && <span className="stable-segment">{item.stableText} </span>}
                                {item.unstableText && <span className="unstable-segment">{item.unstableText}</span>}
                              </>
                            ) : (
                              cleanRepetitions(item.source)
                            )}
                            {item.isPartial && <span className="typing-caret" aria-hidden="true" />}
                          </p>
                        </article>
                      );
                    })}
                  </div>
                </section>

                <section className="language-panel vietnamese-panel" aria-label="Bản dịch">
                  <header><span>🌐</span><div><strong>Bản dịch</strong><small>Xuất hiện sau khi cụm lời gốc ổn định</small></div></header>
                  <div className="language-feed" ref={vietnamesePanelRef}>
                    {subtitles.map((item) => (
                      <article className="language-line translated-line" key={item.id}>
                        <div><time>{clock(item.createdAt)}</time><span>Người {item.speakerId} • Bản dịch</span></div>
                        <p>{item.translated ? cleanRepetitions(item.translated) : <em>Đang dịch…</em>}</p>
                      </article>
                    ))}
                  </div>
                </section>
              </>
            )}
          </div>
        </div>
      )}
    </main>
  );
}
