import type { NextApiRequest, NextApiResponse } from "next";

const ALLOWED_METHODS = new Set(["GET", "POST", "DELETE"]);

function gatewayTimeout(): number {
  const configured = Number(process.env.KENKOMIRAI_GATEWAY_TIMEOUT_MS || "120000");
  return Number.isInteger(configured) && configured >= 1_000 && configured <= 300_000 ? configured : 120_000;
}

export default async function handler(request: NextApiRequest, response: NextApiResponse) {
  const method = request.method || "GET";
  if (!ALLOWED_METHODS.has(method)) {
    response.setHeader("Allow", [...ALLOWED_METHODS].join(", "));
    response.status(405).json({ detail: "method not allowed" });
    return;
  }
  const segments = Array.isArray(request.query.path) ? request.query.path : [];
  if (!segments.length || segments.some((segment) => segment === ".." || segment.includes("/"))) {
    response.status(400).json({ detail: "invalid backend path" });
    return;
  }
  try {
    const upstream = (process.env.KENKOMIRAI_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
    const target = new URL(`${upstream}/api/v1/${segments.map(encodeURIComponent).join("/")}`);
    if (!new Set(["http:", "https:"]).has(target.protocol)) throw new Error("unsupported upstream protocol");
    for (const [key, value] of Object.entries(request.query)) {
      if (key === "path") continue;
      for (const item of Array.isArray(value) ? value : [value]) {
        if (typeof item === "string") target.searchParams.append(key, item);
      }
    }
    const upstreamResponse = await fetch(target, {
      method,
      headers: {
        Accept: "application/json",
        ...(method === "POST" ? { "Content-Type": "application/json" } : {}),
        ...(typeof request.headers["x-request-id"] === "string" ? { "X-Request-ID": request.headers["x-request-id"] } : {}),
      },
      body: method === "POST" ? JSON.stringify(request.body ?? {}) : undefined,
      signal: AbortSignal.timeout(gatewayTimeout()),
    });
    const contentType = upstreamResponse.headers.get("content-type") || "application/json";
    response.status(upstreamResponse.status);
    response.setHeader("Content-Type", contentType);
    const requestId = upstreamResponse.headers.get("x-request-id");
    if (requestId) response.setHeader("X-Request-ID", requestId);
    const retryAfter = upstreamResponse.headers.get("retry-after");
    if (retryAfter) response.setHeader("Retry-After", retryAfter);
    response.setHeader("Cache-Control", "no-store");
    response.send(Buffer.from(await upstreamResponse.arrayBuffer()));
  } catch (error) {
    const timedOut = error instanceof Error && (error.name === "TimeoutError" || error.name === "AbortError");
    response.status(timedOut ? 504 : 502).json({ detail: timedOut ? "backend request timed out" : "backend service unavailable" });
  }
}
