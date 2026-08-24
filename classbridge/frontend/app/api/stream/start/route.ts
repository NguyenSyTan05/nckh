export const runtime = "nodejs";

const AI_SERVICE_URL = process.env.AI_SERVICE_URL ?? "http://127.0.0.1:8000";

export async function GET(request: Request) {
  const joinCode = new URL(request.url).searchParams.get("join_code")?.trim();
  if (!joinCode) {
    return Response.json({ error: "Thiếu mã lớp học." }, { status: 400 });
  }
  try {
    const response = await fetch(
      `${AI_SERVICE_URL}/classroom/join/${encodeURIComponent(joinCode)}`,
      { signal: AbortSignal.any([request.signal, AbortSignal.timeout(10_000)]) },
    );
    const body = await response.text();
    return new Response(body, {
      status: response.status,
      headers: { "content-type": response.headers.get("content-type") ?? "application/json" },
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unknown error";
    return Response.json({ error: "Dịch vụ lớp học chưa sẵn sàng.", detail }, { status: 503 });
  }
}

export async function POST(request: Request) {
  try {
    const formData = await request.formData();
    const response = await fetch(`${AI_SERVICE_URL}/stream/start`, {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    return Response.json(data, { status: response.status });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unknown error";
    return Response.json(
      { error: "Dịch vụ AI chưa sẵn sàng.", detail },
      { status: 503 },
    );
  }
}
