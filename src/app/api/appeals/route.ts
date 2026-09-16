import { openAppeals } from "@/lib/server/appeals.mjs";
import { authorized, isString as string, readJson as body, response, sameOrigin } from "@/lib/server/http";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function GET(request: Request) {
  if (!authorized(request)) return response({ error: "請輸入正確的後台密碼；伺服器需設定 WELFARE_ADMIN_PASSWORD。" }, 401);
  const db = openAppeals(); try { return response(db.list()); } finally { db.close(); }
}
export async function POST(request: Request) {
  if (!sameOrigin(request)) return response({ error: "不接受跨站送出。" }, 403);
  let input;
  try {
    input = await body(request);
    if (!input || !string(input.profileNickname, 100) || !string(input.region, 100) ||
      !(input.profileId === null || string(input.profileId, 100)) ||
      !(input.age === null || Number.isInteger(input.age) && input.age >= 0 && input.age <= 150) ||
      !Array.isArray(input.identities) || input.identities.length > 30 || !input.identities.every((v: unknown) => string(v, 100)) ||
      !string(input.mainRequest, 3000) || !input.mainRequest.trim() || !string(input.summary, 15000) ||
      !Array.isArray(input.transcript) || input.transcript.length > 150 ||
      !input.transcript.every((v: { role: string; text: string }) => v && ["user", "assistant"].includes(v.role) && string(v.text, 10000))) throw new Error();
  } catch { return response({ error: "需求內容格式不正確或過長，請重新確認。" }, 400); }
  const key = request.headers.get("idempotency-key");
  if (!key || !/^[a-zA-Z0-9_-]{16,100}$/.test(key)) return response({ error: "缺少有效的送出識別碼。" }, 400);
  const { profileId, profileNickname, region, identities, age, mainRequest, summary, transcript } = input;
  const db = openAppeals();
  try { return response(db.create({ profileId, profileNickname, region, identities, age, mainRequest, summary, transcript }, key), 201); } finally { db.close(); }
}
export async function PATCH(request: Request) {
  if (!authorized(request)) return response({ error: "後台密碼不正確。" }, 401);
  if (!sameOrigin(request)) return response({ error: "不接受跨站送出。" }, 403);
  let input;
  try { input = await body(request); if (!input || !string(input.id, 100) || !["new", "reviewing", "resolved"].includes(input.status)) throw new Error(); }
  catch { return response({ error: "狀態格式不正確。" }, 400); }
  const db = openAppeals();
  try { return db.update(input.id, input.status) ? response({ ok: true }) : response({ error: "找不到這筆需求。" }, 404); } finally { db.close(); }
}
