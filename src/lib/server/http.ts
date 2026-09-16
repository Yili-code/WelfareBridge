import { timingSafeEqual } from "node:crypto";

/** 需求登記與訴求專區 API 共用的請求工具 */
export const response = (body: unknown, status = 200) => Response.json(body, { status, headers: { "Cache-Control": "no-store" } });

export function authorized(request: Request) {
  const secret = process.env.WELFARE_ADMIN_PASSWORD;
  const supplied = request.headers.get("authorization")?.replace(/^Bearer /, "") || "";
  return !!secret && Buffer.byteLength(secret) === Buffer.byteLength(supplied) && timingSafeEqual(Buffer.from(secret), Buffer.from(supplied));
}

// 以 Host 標頭比對：standalone 伺服器（Docker）的 request.url 會是綁定位址 0.0.0.0，不是瀏覽器看到的網址
export function sameOrigin(request: Request) {
  const origin = request.headers.get("origin");
  if (!origin) return true;
  try { return new URL(origin).host === request.headers.get("host"); } catch { return false; }
}

export async function readJson(request: Request, limit = 100_000) {
  const reader = request.body?.getReader();
  if (!reader) throw new Error("Missing body");
  const chunks: Uint8Array[] = []; let size = 0;
  while (true) {
    const { done, value } = await reader.read(); if (done) break;
    size += value.length; if (size > limit) { await reader.cancel(); throw new Error("Too large"); }
    chunks.push(value);
  }
  return JSON.parse(Buffer.concat(chunks).toString());
}

export const isString = (v: unknown, max = 1000): v is string => typeof v === "string" && v.length <= max;
