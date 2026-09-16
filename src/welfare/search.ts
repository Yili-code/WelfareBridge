import type { BenefitCard, MatchResult, MatchStatus } from "./api";

export type FacetKey = "region" | "domain" | "service_type" | "audiences";
export type Filters = Record<FacetKey, Set<string>>;
export type SortKey = "match" | "title" | "updated";

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

export function searchCards(cards: BenefitCard[], { query, filters, onlyMatch, sort, results }: { query: string; filters: Filters; onlyMatch: boolean; sort: SortKey; results?: Record<string, MatchResult> }) {
  const words = normalize(query).split(/\s+/).filter(Boolean);
  const list = cards.filter(card => {
    for (const { key } of FACETS) {
      const selected = filters[key];
      if (selected.size && !values(card, key).some(value => selected.has(value))) return false;
    }
    if (words.length) {
      const hay = haystack(card);
      if (!words.every(word => hay.includes(word))) return false;
    }
    if (onlyMatch && results && (results[card.id]?.status ?? "no") === "no") return false;
    return true;
  });
  return list.sort((a, b) => {
    if (sort === "title") return a.title.localeCompare(b.title, "zh-Hant");
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
