"""登錄表載入器：attribute_registry.yaml + attribute_aliases_mined.yaml + taxonomy.yaml + identity_ontology.yaml。

提供：
- 屬性查詢、型態／operator 相容檢查、別名索引（原文 → 屬性候選）
- 類別 → 領域、葉節點清單、標籤
- 身分本體：別名 → 標籤、implies 展開、標籤 → profile 屬性
- 推導屬性計算（只允許四則運算、比較與 poverty_line(city)）
- 同步到 MongoDB（attribute_registry / taxonomy / identity_ontology 三個集合，供前端顯示）
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from ..config import Settings, get_settings
from ..services.normalization import CITIES, normalize_city, normalize_text

log = logging.getLogger(__name__)

TYPES = {"number", "boolean", "enum", "multi_enum", "city", "date", "text"}
OPERATORS_BY_TYPE: dict[str, set[str]] = {
    "number": {"=", "!=", ">", ">=", "<", "<=", "between", "exists"},
    "boolean": {"=", "!=", "exists"},
    "enum": {"=", "!=", "in", "not_in", "exists"},
    "multi_enum": {"contains", "in", "not_in", "exists"},
    "city": {"=", "!=", "in", "not_in", "exists"},
    "date": {"=", ">", ">=", "<", "<=", "between", "exists"},
    "text": {"=", "!=", "in", "not_in", "contains", "exists"},
}
ORDERED_EXTRA = {">", ">=", "<", "<="}
SAFE_EXPR_RE = re.compile(r"^[A-Za-z0-9_.\s+\-*/()><=!]+$")


@dataclass
class Attribute:
    id: str
    type: str
    label: str
    question: str = ""
    help: str = ""
    values: list[dict] = field(default_factory=list)
    ordered: bool = False
    unit: str = ""
    domains: list[str] = field(default_factory=lambda: ["all"])
    aliases: list[str] = field(default_factory=list)
    mined_aliases: list[dict] = field(default_factory=list)
    sensitivity: str = "low"
    hard_filter: bool = False
    ask_priority: int = 50
    derived: str = ""
    deprecated: bool = False
    replaced_by: str = ""
    since_version: int = 1

    @property
    def namespace(self) -> str:
        return self.id.split(".", 1)[0]

    @property
    def allowed_operators(self) -> set[str]:
        ops = set(OPERATORS_BY_TYPE.get(self.type, {"=", "!="}))
        if self.type == "enum" and self.ordered:
            ops |= ORDERED_EXTRA
        return ops

    @property
    def value_list(self) -> list[str]:
        return [str(v.get("value")) for v in self.values]

    def value_label(self, value: Any) -> str:
        for item in self.values:
            if str(item.get("value")) == str(value):
                return str(item.get("label", value))
        return str(value)

    def all_aliases(self, *, include_mined: bool = False, min_mined_z: float = 3.0) -> list[str]:
        names = [self.label, *self.aliases]
        if include_mined:
            names.extend(m["term"] for m in self.mined_aliases if float(m.get("z", 0)) >= min_mined_z)
        seen: list[str] = []
        for name in names:
            if name and name not in seen:
                seen.append(name)
        return seen

    def question_type(self) -> str:
        return {"number": "number", "boolean": "boolean", "enum": "single_choice", "multi_enum": "multi_choice", "city": "city", "date": "text", "text": "text"}[self.type]

    def to_dict(self) -> dict:
        return {
            "id": self.id, "type": self.type, "label": self.label, "question": self.question, "help": self.help, "values": self.values, "ordered": self.ordered,
            "unit": self.unit, "domains": self.domains, "aliases": self.aliases, "mined_aliases": self.mined_aliases, "sensitivity": self.sensitivity,
            "hard_filter": self.hard_filter, "ask_priority": self.ask_priority, "derived": self.derived, "deprecated": self.deprecated, "replaced_by": self.replaced_by,
            "namespace": self.namespace, "question_type": self.question_type(), "since_version": self.since_version,
        }


@dataclass
class TaxonomyNode:
    id: str
    label: str
    description: str = ""
    parent: str = ""
    domain: str = ""
    need_types: list[str] = field(default_factory=list)
    default_benefit_form: str = ""
    children: list[str] = field(default_factory=list)

    @property
    def is_leaf(self) -> bool:
        return not self.children

    def to_dict(self) -> dict:
        return {"id": self.id, "label": self.label, "description": self.description, "parent": self.parent, "domain": self.domain, "need_types": self.need_types, "default_benefit_form": self.default_benefit_form, "children": self.children, "is_leaf": self.is_leaf}


@dataclass
class IdentityTag:
    id: str
    label: str
    aliases: list[str] = field(default_factory=list)
    attribute: str = ""
    implies: list[str] = field(default_factory=list)
    virtual: bool = False
    basis: str = ""

    def to_dict(self) -> dict:
        return {"id": self.id, "label": self.label, "aliases": self.aliases, "attribute": self.attribute, "implies": self.implies, "virtual": self.virtual, "basis": self.basis}


class Registry:
    def __init__(self, attributes: list[Attribute], taxonomy: list[TaxonomyNode], tags: list[IdentityTag], *, version: int = 1, taxonomy_version: int = 1, poverty: dict | None = None):
        self.version = version
        self.taxonomy_version = taxonomy_version
        self.attributes: dict[str, Attribute] = {a.id: a for a in attributes}
        self.taxonomy: dict[str, TaxonomyNode] = {n.id: n for n in taxonomy}
        self.tags: dict[str, IdentityTag] = {t.id: t for t in tags}
        self.poverty = poverty or {"verified": False, "values": {}}
        self._alias_index: list[tuple[str, str, str]] | None = None  # (normalized alias, attribute id, original alias)
        self._alias_index_mined: list[tuple[str, str, str]] | None = None
        self._tag_alias_index: list[tuple[str, str, str]] | None = None
        self._label_to_tag: dict[str, str] = {t.label: t.id for t in tags}

    # ------------------------------------------------------------ attributes
    def get(self, attribute_id: str) -> Attribute | None:
        return self.attributes.get(attribute_id)

    def has(self, attribute_id: str) -> bool:
        return attribute_id in self.attributes

    def askable(self) -> list[Attribute]:
        return [a for a in self.attributes.values() if not a.derived and not a.deprecated and a.ask_priority > 0]

    def for_domains(self, domains: list[str] | None) -> list[Attribute]:
        if not domains:
            return list(self.attributes.values())
        wanted = set(domains)
        return [a for a in self.attributes.values() if "all" in a.domains or wanted & set(a.domains)]

    def alias_index(self, *, include_mined: bool = False) -> list[tuple[str, str, str]]:
        cached = self._alias_index_mined if include_mined else self._alias_index
        if cached is None:
            entries: list[tuple[str, str, str]] = []
            for attribute in self.attributes.values():
                if attribute.deprecated:
                    continue
                for alias in attribute.all_aliases(include_mined=include_mined):
                    norm = normalize_text(alias)
                    if len(norm) >= 2:
                        entries.append((norm, attribute.id, alias))
            entries.sort(key=lambda e: len(e[0]), reverse=True)
            if include_mined:
                self._alias_index_mined = entries
            else:
                self._alias_index = entries
            cached = entries
        return cached

    def attributes_in_text(self, text: str, *, include_mined: bool = False) -> dict[str, list[str]]:
        """回傳 {attribute_id: [命中的別名...]}（原文正規化後子字串比對；長別名優先）。
        include_mined=True 時也用語料統計出的別名（只適合當 AI 候選，不適合直接產生規則）。"""
        norm = normalize_text(text)
        hits: dict[str, list[str]] = {}
        for alias_norm, attribute_id, alias in self.alias_index(include_mined=include_mined):
            if alias_norm in norm:
                hits.setdefault(attribute_id, [])
                if alias not in hits[attribute_id]:
                    hits[attribute_id].append(alias)
        return hits

    def operator_allowed(self, attribute_id: str, operator: str) -> bool:
        attribute = self.get(attribute_id)
        return bool(attribute) and operator in attribute.allowed_operators

    def enum_rank(self, attribute_id: str, value: Any) -> int | None:
        attribute = self.get(attribute_id)
        if attribute is None or attribute.type != "enum" or not attribute.ordered:
            return None
        values = attribute.value_list
        return values.index(str(value)) if str(value) in values else None

    # ------------------------------------------------------------- taxonomy
    def leaves(self) -> list[TaxonomyNode]:
        return [n for n in self.taxonomy.values() if n.is_leaf]

    def domains(self) -> list[TaxonomyNode]:
        return [n for n in self.taxonomy.values() if not n.parent]

    def category(self, category_id: str) -> TaxonomyNode | None:
        return self.taxonomy.get(category_id)

    def domain_of(self, category_id: str) -> str:
        node = self.taxonomy.get(category_id)
        return node.domain if node else ""

    def category_label(self, category_id: str) -> str:
        node = self.taxonomy.get(category_id)
        return node.label if node else category_id

    def domain_label(self, domain_id: str) -> str:
        node = self.taxonomy.get(domain_id)
        return node.label if node else domain_id

    def categories_for_need(self, need_type: str | None) -> set[str]:
        if not need_type or need_type == "unknown":
            return {n.id for n in self.leaves()}
        return {n.id for n in self.leaves() if need_type in n.need_types}

    # ------------------------------------------------------------- identity
    def tag_alias_index(self) -> list[tuple[str, str, str]]:
        if self._tag_alias_index is None:
            entries = []
            for tag in self.tags.values():
                for alias in [tag.label, *tag.aliases]:
                    norm = normalize_text(alias)
                    if len(norm) >= 2:
                        entries.append((norm, tag.id, alias))
            entries.sort(key=lambda e: len(e[0]), reverse=True)
            self._tag_alias_index = entries
        return self._tag_alias_index

    def tags_in_text(self, text: str) -> dict[str, str]:
        """{tag_id: 命中的別名}"""
        norm = normalize_text(text)
        hits: dict[str, str] = {}
        for alias_norm, tag_id, alias in self.tag_alias_index():
            if tag_id not in hits and alias_norm in norm:
                hits[tag_id] = alias
        return hits

    def tag_for_label(self, label: str) -> IdentityTag | None:
        tag_id = self._label_to_tag.get(label)
        if tag_id:
            return self.tags[tag_id]
        for tag in self.tags.values():
            if label in tag.aliases:
                return tag
        return None

    def expand_tags(self, tag_ids: set[str]) -> set[str]:
        """implies 閉包：具備低收入戶 → 也具備清寒、弱勢學生。"""
        result = set(tag_ids)
        changed = True
        while changed:
            changed = False
            for tag_id in list(result):
                tag = self.tags.get(tag_id)
                if not tag:
                    continue
                for implied in tag.implies:
                    if implied not in result:
                        result.add(implied)
                        changed = True
        return result

    def tag_attribute(self, tag_id: str) -> str:
        tag = self.tags.get(tag_id)
        return tag.attribute if tag else ""

    def tags_from_attribute_values(self, values: dict[str, Any]) -> tuple[set[str], bool]:
        """由 profile 屬性值推出使用者具備的身分標籤；回傳 (標籤集合, 是否回答過任何身分題)。"""
        answered = False
        tags: set[str] = set()
        for tag in self.tags.values():
            if not tag.attribute:
                continue
            value = values.get(tag.attribute)
            if value is None:
                continue
            answered = True
            attribute = self.get(tag.attribute)
            if attribute and attribute.type == "boolean" and value is True:
                tags.add(tag.id)
            elif attribute and attribute.type == "enum" and str(value) == tag.label:
                tags.add(tag.id)
            elif attribute and attribute.type == "enum" and tag.id == "yami" and str(value) == "雅美族":
                tags.add(tag.id)
        return self.expand_tags(tags), answered

    # -------------------------------------------------------------- derived
    def poverty_line(self, city: str | None) -> float | None:
        if not self.poverty.get("verified"):
            return None
        values = self.poverty.get("values") or {}
        key = normalize_city(city or "") or ""
        value = values.get(key) if key else None
        if value is None:
            value = values.get("臺灣省")
        return float(value) if value else None

    def evaluate_derived(self, attribute: Attribute, values: dict[str, Any]) -> Any:
        """推導屬性：表達式只含屬性 id、數字、四則、比較與 poverty_line(attr)。缺任一輸入 → None。"""
        expr = attribute.derived
        if not expr or not SAFE_EXPR_RE.match(expr):
            return None
        namespace: dict[str, Any] = {}
        ids = sorted(re.findall(r"[a-z_]+\.[a-z_]+", expr), key=len, reverse=True)
        rewritten = expr
        for index, attribute_id in enumerate(ids):
            value = values.get(attribute_id)
            if value is None:
                return None
            token = f"__v{index}"
            namespace[token] = value
            rewritten = rewritten.replace(attribute_id, token)

        def _poverty(city_value: Any) -> Any:
            line = self.poverty_line(city_value if isinstance(city_value, str) else None)
            if line is None:
                raise ValueError("poverty line not verified")
            return line

        try:
            result = eval(rewritten, {"__builtins__": {}}, {**namespace, "poverty_line": _poverty})  # noqa: S307 - 受限表達式（登錄表為信任來源）
        except Exception:
            return None
        if isinstance(result, bool):
            return result
        if isinstance(result, (int, float)):
            return round(float(result), 3)
        return None

    # ---------------------------------------------------------------- misc
    def catalog(self) -> dict[str, dict]:
        """前端表單／追問用的欄位目錄（相容 v1 FIELD_CATALOG 形狀）。"""
        result: dict[str, dict] = {}
        for attribute in self.attributes.values():
            if attribute.deprecated:
                continue
            options: list[dict] = []
            if attribute.type in {"enum", "multi_enum"}:
                options = [{"value": v.get("value"), "label": v.get("label", v.get("value"))} for v in attribute.values]
            elif attribute.type == "boolean":
                options = [{"value": True, "label": "是"}, {"value": False, "label": "否"}]
            elif attribute.type == "city":
                options = [{"value": c, "label": c} for c in CITIES]
            result[attribute.id] = {
                "label": attribute.label, "question": attribute.question, "help": attribute.help, "type": attribute.question_type(), "options": options,
                "namespace": attribute.namespace, "domains": attribute.domains, "sensitivity": attribute.sensitivity, "unit": attribute.unit,
                "derived": bool(attribute.derived), "hard_filter": attribute.hard_filter, "ask_priority": attribute.ask_priority,
            }
        return result

    def sync_to_mongo(self, db) -> dict:
        from ..db import utcnow

        now = utcnow()
        for attribute in self.attributes.values():
            db.attribute_registry.update_one({"_id": attribute.id}, {"$set": {**attribute.to_dict(), "registry_version": self.version, "synced_at": now}}, upsert=True)
        for node in self.taxonomy.values():
            db.taxonomy.update_one({"_id": node.id}, {"$set": {**node.to_dict(), "taxonomy_version": self.taxonomy_version, "synced_at": now}}, upsert=True)
        for tag in self.tags.values():
            db.identity_ontology.update_one({"_id": tag.id}, {"$set": {**tag.to_dict(), "synced_at": now}}, upsert=True)
        db.app_meta.update_one({"_id": "registry"}, {"$set": {"registry_version": self.version, "taxonomy_version": self.taxonomy_version, "attributes": len(self.attributes), "categories": len(self.leaves()), "tags": len(self.tags), "synced_at": now}}, upsert=True)
        return {"attributes": len(self.attributes), "taxonomy": len(self.taxonomy), "tags": len(self.tags)}


# ---------------------------------------------------------------- loading
def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _walk_taxonomy(nodes: list[dict], parent: str, domain: str, out: list[TaxonomyNode]) -> None:
    for raw in nodes:
        node_id = raw["id"]
        root = domain or node_id
        node = TaxonomyNode(id=node_id, label=raw.get("label", node_id), description=raw.get("description", ""), parent=parent, domain=root, need_types=list(raw.get("need_types") or []), default_benefit_form=raw.get("default_benefit_form", ""), children=[c["id"] for c in raw.get("children") or []])
        out.append(node)
        _walk_taxonomy(raw.get("children") or [], node_id, root, out)


def load_registry(settings: Settings | None = None) -> Registry:
    settings = settings or get_settings()
    registry_yaml = _load_yaml(settings.attribute_registry_file)
    mined_yaml = _load_yaml(settings.attribute_aliases_mined_file)
    mined = {entry["id"]: entry.get("aliases", []) for entry in mined_yaml.get("attributes", []) or []}
    attributes: list[Attribute] = []
    for raw in registry_yaml.get("attributes", []) or []:
        if raw.get("type") not in TYPES:
            log.warning("attribute %s has unknown type %s", raw.get("id"), raw.get("type"))
            continue
        attributes.append(
            Attribute(
                id=raw["id"], type=raw["type"], label=raw.get("label", raw["id"]), question=raw.get("question", ""), help=raw.get("help", ""),
                values=list(raw.get("values") or []), ordered=bool(raw.get("ordered", False)), unit=raw.get("unit", "") or "", domains=list(raw.get("domains") or ["all"]),
                aliases=list(raw.get("aliases") or []), mined_aliases=list(mined.get(raw["id"], [])), sensitivity=raw.get("sensitivity", "low"), hard_filter=bool(raw.get("hard_filter", False)),
                ask_priority=int(raw.get("ask_priority", 50)), derived=raw.get("derived", "") or "", deprecated=bool(raw.get("deprecated", False)), replaced_by=raw.get("replaced_by", "") or "",
                since_version=int(raw.get("since_version", 1)),
            )
        )
    taxonomy_yaml = _load_yaml(settings.taxonomy_file)
    nodes: list[TaxonomyNode] = []
    _walk_taxonomy(taxonomy_yaml.get("domains", []) or [], "", "", nodes)
    ontology_yaml = _load_yaml(settings.identity_ontology_file)
    tags = [IdentityTag(id=t["id"], label=t.get("label", t["id"]), aliases=list(t.get("aliases") or []), attribute=t.get("attribute", "") or "", implies=list(t.get("implies") or []), virtual=bool(t.get("virtual", False)), basis=t.get("basis", "") or "") for t in ontology_yaml.get("tags", []) or []]
    poverty = _load_yaml(settings.resolve_path("app/registry/poverty_line.yaml"))
    return Registry(attributes, nodes, tags, version=int(registry_yaml.get("version", 1)), taxonomy_version=int(taxonomy_yaml.get("version", 1)), poverty=poverty)


@lru_cache
def get_registry() -> Registry:
    return load_registry()


def reset_registry() -> None:
    get_registry.cache_clear()
