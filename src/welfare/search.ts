import type { BenefitCard, MatchResult, MatchStatus } from "./api";
import { compareDeadline } from "./deadline";

export type FacetKey = "region" | "domain" | "service_type" | "audiences";
export type Filters = Record<FacetKey, Set<string>>;
export type SortKey = "match" | "deadline" | "title" | "updated";

export const FACETS: { key: FacetKey; label: string; show: number }[] = [
  { key: "region", label: "地區", show: 8 },
  { key: "domain", label: "補助領域", show: 8 },
  { key: "service_type", label: "補助類型", show: 10 },
  { key: "audiences", label: "適用對象", show: 10 },
];

export const emptyFilters = (): Filters => ({ region: new Set(), domain: new Set(), service_type: new Set(), audiences: new Set() });

const values = (card: BenefitCard, key: FacetKey) => (key === "audiences" ? card.audiences : [card[key]]).filter(Boolean);
const normalize = (text: string) => text.toLowerCase().replace(/台/g, "臺");

export function facetCounts(cards: BenefitCard[], key: FacetKey) {
  const counts = new Map<string, number>();
  for (const card of cards) for (const value of values(card, key)) counts.set(value, (counts.get(value) ?? 0) + 1);
  return [...counts.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0], "zh-Hant"));
}

function haystack(card: BenefitCard) {
  return normalize([card.title, card.agency, card.region, card.domain, card.service_type, ...card.audiences, ...card.points].join(" "));
}

const ORDER: Record<MatchStatus, number> = { yes: 0, maybe: 1, no: 2 };

// 與後端 guidance.TOPICS 相同的日常說法：整句話（「我媽媽失智需要人照顧」）拆成需求詞，任一個出現就算符合
const NEED_WORDS = ["就學", "學費", "獎學金", "助學", "學貸", "租屋", "房租", "租金", "住宅", "買房", "購屋", "房貸", "修繕", "失業", "求職", "職訓", "裁員", "資遣", "找工作", "轉職", "創業", "離職", "醫療", "健保", "看病", "就醫", "住院", "重病", "手術", "身障", "身心障礙", "殘障", "輔具", "早療", "發展遲緩", "長照", "照顧", "照護", "失智", "看護", "居家服務", "日間照顧", "老人", "長輩", "臥床", "生活費", "育兒", "急難", "缺錢", "單親", "托育", "育嬰", "生育", "津貼", "低收", "撫養", "喪葬"];

// 公告用字和日常說法不同：搜「獎學金」也要找到標題寫「獎助學金」的補助
const SYNONYMS: Record<string, string[]> = { "獎學金": ["獎助學金", "獎學", "助學"], "助學": ["獎助學金", "助學金"], "學費": ["學雜費", "就學"], "租屋": ["租金", "租賃"], "房租": ["租金", "租賃"] };
const expand = (terms: string[]) => [...new Set(terms.flatMap(term => [term, ...(SYNONYMS[term] ?? [])]))];

/** 整句說法（「我需要獎學金」）去掉開頭的「我需要／想找」等贅詞後再比對 */
const stripFiller = (word: string) => word.replace(/^(請問|請|幫我)?(我)?(需要|想要|想找|想|要|找|有沒有|有)?/, "").replace(/(的)?(補助|服務|資訊)$/, "") || word;

/** 句中有需求詞就用需求詞（任一個出現即可，含同義說法）；沒有需求詞才去掉贅詞後照原樣比對 */
function queryGroups(query: string): string[][] {
  return normalize(query).split(/\s+/).filter(Boolean).map(word => {
    const found = NEED_WORDS.filter(term => word.includes(term));
    if (found.length && word.length > 6) return expand(found);
    const core = stripFiller(word);
    const inCore = NEED_WORDS.filter(term => core.includes(term));
    return inCore.length && core.length > 6 ? expand(inCore) : expand([core]);
  });
}

export function searchCards(cards: BenefitCard[], { query, filters, onlyMatch, sort, results }: { query: string; filters: Filters; onlyMatch: boolean; sort: SortKey; results?: Record<string, MatchResult> }) {
  const groups = queryGroups(query);
  const list = cards.filter(card => {
    for (const { key } of FACETS) {
      const selected = filters[key];
      if (selected.size && !values(card, key).some(value => selected.has(value))) return false;
    }
    if (groups.length) {
      const hay = haystack(card);
      if (!groups.every(group => group.some(word => hay.includes(word)))) return false;
    }
    if (onlyMatch && results && (results[card.id]?.status ?? "no") === "no") return false;
    return true;
  });
  return list.sort((a, b) => {
    if (sort === "title") return a.title.localeCompare(b.title, "zh-Hant");
    if (sort === "deadline") return compareDeadline(a, b) || a.title.localeCompare(b.title, "zh-Hant");
    if (sort === "updated") return (b.updated || "").localeCompare(a.updated || "") || a.title.localeCompare(b.title, "zh-Hant");
    if (results) {
      const diff = ORDER[results[a.id]?.status ?? "no"] - ORDER[results[b.id]?.status ?? "no"];
      if (diff) return diff;
      const needs = (results[a.id]?.needs.length ?? 0) - (results[b.id]?.needs.length ?? 0);
      if (needs) return needs;
    }
    return a.title.localeCompare(b.title, "zh-Hant");
  });
}
