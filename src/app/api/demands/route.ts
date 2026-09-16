import { DEMAND_TYPES } from "@/lib/demand-types";
import { openDemands } from "@/lib/server/demands.mjs";
import { isString, readJson, response, sameOrigin } from "@/lib/server/http";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const voterOf = (value: unknown) => (isString(value, 64) && /^[a-zA-Z0-9_-]{16,64}$/.test(value) ? value : "");

/** 公開的訴求清單：不含任何個人資料，只有訴求本身 */
export async function GET(request: Request) {
  const voter = voterOf(new URL(request.url).searchParams.get("voter"));
  const db = openDemands();
  try { return response({ items: db.list(voter) }); } finally { db.close(); }
}

export async function POST(request: Request) {
  if (!sameOrigin(request)) return response({ error: "不接受跨站送出。" }, 403);
  let input;
  try {
    input = await readJson(request, 20_000);
    if (!input || !isString(input.title, 80) || input.title.trim().length < 4 || !DEMAND_TYPES.includes(input.type) || !isString(input.region, 40) || !isString(input.detail, 1000)) throw new Error();
  } catch { return response({ error: "請填寫至少 4 個字的訴求標題，並選擇服務類型；說明請在 1000 字以內。" }, 400); }
  const voter = voterOf(input.voter);
  if (!voter) return response({ error: "缺少瀏覽器識別碼，請重新整理頁面後再送出。" }, 400);
  const db = openDemands();
  try {
    const item = db.create({ title: input.title.trim(), type: input.type, region: input.region.trim() || "未填寫地區", detail: input.detail.trim() }, voter);
    return response({ item }, 201);
  } finally { db.close(); }
}
