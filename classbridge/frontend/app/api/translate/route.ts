export const runtime = "nodejs";

const AI_SERVICE_URL = process.env.AI_SERVICE_URL ?? "http://127.0.0.1:8000";

export async function POST(request: Request) {
  try {
    const payload = (await request.json()) as {
      text?: string;
      source_language?: "en" | "vi";
    };
    const text = payload.text?.trim();
    if (!text) return Response.json({ error: "Thiếu nội dung cần dịch." }, { status: 400 });

    const upstream = new URLSearchParams();
    upstream.append("text", text);
    upstream.append("source_language", payload.source_language ?? "en");
    const response = await fetch(`${AI_SERVICE_URL}/v1/translate`, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: upstream.toString(),
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(120_000)]),
    });
    const body = await response.text();
    return new Response(body, {
      status: response.status,
      headers: { "content-type": response.headers.get("content-type") ?? "application/json" },
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unknown error";
    return Response.json({ error: "Không thể dịch nội dung.", detail }, { status: 503 });
  }
}
