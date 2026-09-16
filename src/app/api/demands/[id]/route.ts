import { openDemands } from "@/lib/server/demands.mjs";
import { authorized, isString, readJson, response, sameOrigin } from "@/lib/server/http";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/** 附議：同一個瀏覽器對同一則訴求只算一次 */
export async function POST(request: Request, ctx: RouteContext<"/api/demands/[id]">) {
  if (!sameOrigin(request)) return response({ error: "不接受跨站送出。" }, 403);
  const { id } = await ctx.params;
  let voter = "";
  try {
    const input = await readJson(request, 2_000);
    if (isString(input?.voter, 64) && /^[a-zA-Z0-9_-]{16,64}$/.test(input.voter)) voter = input.voter;
  } catch { /* 下面統一回應 */ }
  if (!voter) return response({ error: "缺少瀏覽器識別碼，請重新整理頁面後再試。" }, 400);
  const db = openDemands();
  try {
    const item = db.support(id, voter);
    return item ? response({ item }) : response({ error: "找不到這則訴求。" }, 404);
  } finally { db.close(); }
}

/** 承辦人員更新狀態：open（蒐集中／待認領）、claimed（已認領）、done（已實現） */
export async function PATCH(request: Request, ctx: RouteContext<"/api/demands/[id]">) {
  if (!authorized(request)) return response({ error: "後台密碼不正確。" }, 401);
  if (!sameOrigin(request)) return response({ error: "不接受跨站送出。" }, 403);
  const { id } = await ctx.params;
  let input;
  try {
    input = await readJson(request, 5_000);
    if (!input || !["open", "claimed", "done"].includes(input.status) || !isString(input.owner ?? "", 80) || !isString(input.result ?? "", 500)) throw new Error();
  } catch { return response({ error: "狀態格式不正確。" }, 400); }
  const db = openDemands();
  try {
    return db.update(id, { status: input.status, owner: (input.owner ?? "").trim(), result: (input.result ?? "").trim() }) ? response({ ok: true }) : response({ error: "找不到這則訴求。" }, 404);
  } finally { db.close(); }
}
