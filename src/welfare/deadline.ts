/** 申請期限的顯示：「還有 N 天截止」「隨時可申請」，以及依截止日排序。日期以使用者裝置的當地日期計算。 */

export type DeadlineTone = "urgent" | "soon" | "normal" | "open" | "past";

export function localToday(now = new Date()) {
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}-${String(now.getDate()).padStart(2, "0")}`;
}

/** 距離截止還有幾天（今天截止＝0，已過＝負數）；沒有截止日回傳 null */
export function daysLeft(deadline: string, today = localToday()): number | null {
  const parse = (value: string) => {
    const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value);
    return match ? Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])) : null;
  };
  const end = parse(deadline);
  const start = parse(today);
  return end === null || start === null ? null : Math.round((end - start) / 86_400_000);
}

export function deadlineInfo(item: { deadline: string; rolling: boolean }, today = localToday()): { label: string; tone: DeadlineTone; days: number | null } | null {
  const days = item.deadline ? daysLeft(item.deadline, today) : null;
  if (days !== null) {
    if (days < 0) return { label: "已截止", tone: "past", days };
    if (days === 0) return { label: "今天截止", tone: "urgent", days };
    if (days <= 7) return { label: `還有 ${days} 天截止`, tone: "urgent", days };
    if (days <= 30) return { label: `還有 ${days} 天截止`, tone: "soon", days };
    const [, month, day] = item.deadline.split("-").map(Number);
    return { label: `${month} 月 ${day} 日截止`, tone: "normal", days };
  }
  return item.rolling ? { label: "隨時可申請", tone: "open", days: null } : null;
}

/** 截止日近的在前；隨時可申請的其次；沒寫期限的最後 */
export function compareDeadline(a: { deadline: string; rolling: boolean }, b: { deadline: string; rolling: boolean }, today = localToday()) {
  const rank = (item: { deadline: string; rolling: boolean }) => {
    const days = item.deadline ? daysLeft(item.deadline, today) : null;
    if (days !== null && days >= 0) return days;
    return item.rolling ? 100_000 : 200_000;
  };
  return rank(a) - rank(b);
}
