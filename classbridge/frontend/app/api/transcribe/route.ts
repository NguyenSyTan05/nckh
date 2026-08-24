export const runtime = "nodejs";

const AI_SERVICE_URL = process.env.AI_SERVICE_URL ?? "http://127.0.0.1:8000";

export async function POST(request: Request) {
  try {
    const contentType = request.headers.get("content-type");
    if (!contentType || !contentType.includes("multipart/form-data")) {
      return Response.json({ error: "Yêu cầu phải có dạng multipart/form-data." }, { status: 400 });
    }

    const body = await request.arrayBuffer();
    if (body.byteLength === 0) {
      return Response.json({ error: "Thiếu dữ liệu âm thanh." }, { status: 400 });
    }

    const response = await fetch(`${AI_SERVICE_URL}/v1/transcribe`, {
      method: "POST",
      headers: {
        "content-type": contentType,
      },
      body,
      // Local CPU inference can take several seconds for a full speech segment.
      signal: AbortSignal.any([request.signal, AbortSignal.timeout(120_000)]),
    });
    const responseBody = await response.text();
    return new Response(responseBody, {
      status: response.status,
      headers: { "content-type": response.headers.get("content-type") ?? "application/json" },
    });
  } catch (error) {
    const detail = error instanceof Error ? error.message : "Unknown error";
    return Response.json(
      { error: "Dịch vụ AI chưa sẵn sàng. Hãy khởi động ai-service.", detail },
      { status: 503 },
    );
  }
}


