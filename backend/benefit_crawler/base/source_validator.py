"""Official Source Validation：判斷一個 URL 是否為官方來源。

判斷依據（見 benefit_crawler/config/official_domains.yaml）：
    domain suffix（gov.tw / gov.taipei / edu.tw）+ 明確白名單 + 公立學校網域 + HTTPS + 頁面 title metadata
無法確認 → verified=False, status=needs_review，資料不得進正式資料表。
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

import yaml


@dataclass
class ValidationResult:
    url: str
    domain: str
    https: bool
    verified: bool
    status: str  # verified | needs_review
    method: str
    domain_type: str = "unknown"  # government | education | school | unknown
    organization: str = ""
    provider_type: str = "unknown"
    source_type: str = "government_site"
    title_check: bool | None = None
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class SourceValidator:
    def __init__(self, rules_path: str | Path):
        with open(rules_path, encoding="utf-8") as handle:
            rules = yaml.safe_load(handle) or {}
        self.suffix_rules: list[dict] = rules.get("suffix_rules", [])
        self.whitelist: dict[str, dict] = rules.get("whitelist", {}) or {}
        self.public_school_domains: list[str] = rules.get("public_school_domains", []) or []
        self.blocklist: dict[str, str] = rules.get("blocklist", {}) or {}

    @staticmethod
    def _host_matches(host: str, suffix: str) -> bool:
        return host == suffix or host.endswith("." + suffix)

    def validate_url(
        self,
        url: str,
        *,
        expected_title_keywords: list[str] | None = None,
        page_title: str | None = None,
    ) -> ValidationResult:
        parts = urlsplit(url)
        host = parts.netloc.lower().split(":")[0]
        https = parts.scheme == "https"
        reasons: list[str] = []
        methods: list[str] = []
        domain_type = "unknown"
        organization = ""
        provider_type = "unknown"
        source_type = "government_site"
        verified = False

        if host in self.blocklist:
            reasons.append(f"{host} 在非官方來源清單：{self.blocklist[host]}")
            return ValidationResult(url=url, domain=host, https=https, verified=False, status="needs_review", method="blocklist", domain_type="unknown", reasons=reasons)
        if host in self.whitelist:
            entry = self.whitelist[host]
            organization = entry.get("organization", "")
            provider_type = entry.get("provider_type", "unknown")
            source_type = entry.get("source_type", "government_site")
            domain_type = "school" if provider_type == "school" else "government"
            verified = True
            methods.append("manual_whitelist")
            reasons.append(f"{host} 在官方網域白名單（{organization}）")
        else:
            for rule in self.suffix_rules:
                suffix = rule.get("suffix", "")
                if not suffix or not self._host_matches(host, suffix):
                    continue
                rule_type = rule.get("domain_type", "unknown")
                if rule_type == "government":
                    verified = True
                    domain_type = "government"
                    provider_type = "local_government" if host.count(".") >= 2 and "gov.tw" in host else "central_government"
                    methods.append(f"domain_suffix:{suffix}")
                    reasons.append(f"{host} 屬於政府網域 *.{suffix}")
                elif rule_type == "education":
                    matched_school = next((d for d in self.public_school_domains if self._host_matches(host, d)), None)
                    if matched_school:
                        verified = True
                        domain_type = "school"
                        provider_type = "school"
                        source_type = "school_site"
                        methods.append(f"public_school_domain:{matched_school}")
                        reasons.append(f"{host} 屬於公立學校網域 {matched_school}")
                    else:
                        domain_type = "education"
                        reasons.append(f"{host} 是 edu.tw 網域，但不在政府白名單或公立學校清單，需人工確認")
                break
            else:
                reasons.append(f"{host} 不屬於 gov.tw / gov.taipei / edu.tw，也不在白名單")

        if not https:
            verified = False
            reasons.append("非 HTTPS 連線")
        else:
            methods.append("https")

        title_check: bool | None = None
        if page_title is not None and expected_title_keywords:
            title_check = any(keyword in page_title for keyword in expected_title_keywords)
            methods.append("title_metadata")
            if title_check:
                reasons.append(f"頁面標題含機關關鍵字：{page_title.strip()[:60]}")
            else:
                verified = False
                reasons.append(f"頁面標題「{page_title.strip()[:60]}」不含預期機關關鍵字 {expected_title_keywords}")

        return ValidationResult(
            url=url,
            domain=host,
            https=https,
            verified=verified,
            status="verified" if verified else "needs_review",
            method=" + ".join(methods) if methods else "none",
            domain_type=domain_type,
            organization=organization,
            provider_type=provider_type,
            source_type=source_type,
            title_check=title_check,
            reasons=reasons,
        )
