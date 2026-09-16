"""應用程式設定：由環境變數或 backend/.env 讀入（pydantic-settings）。

所有相對路徑一律以 backend/ 目錄為基準，避免因啟動目錄不同而找不到設定檔。
v2：資料庫改為 MongoDB；LLM 只支援本地 Ollama（none = 純規則式）。
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(PROJECT_DIR / ".env"), str(BACKEND_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Benefits AI API"
    app_version: str = "2.0.0"
    log_level: str = "INFO"

    # ---- MongoDB ----
    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db: str = "benefits"
    # Redis：空字串代表不使用（crawler 觸發改用背景執行緒）
    redis_url: str = ""

    # 逗號分隔。開發預設允許 Vite dev server；正式環境請用環境變數覆寫。
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    # ---- 資料目錄 ----
    data_dir: str = "../data"
    demo_seed_path: str = "../data/demo/seed_v2.json"
    # 舊版（v1 SQL）seed：只用來把原始文件匯入 MongoDB 重新解析
    legacy_seed_path: str = "../data/demo/demo_seed.json"
    demo_seed_on_startup: bool = True
    crawl_on_startup: bool = False

    # ---- 設定檔 ----
    sources_config_path: str = "benefit_crawler/config/sources.yaml"
    official_domains_path: str = "benefit_crawler/config/official_domains.yaml"
    # 由語料統計產生（scripts/mine_keywords.py）；不存在時用 keyword_rules_seed.yaml
    keyword_rules_path: str = "benefit_crawler/config/keyword_rules_v2.yaml"
    keyword_rules_seed_path: str = "benefit_crawler/config/keyword_rules_seed.yaml"
    attribute_registry_path: str = "app/registry/attribute_registry.yaml"
    attribute_aliases_mined_path: str = "app/registry/attribute_aliases_mined.yaml"
    taxonomy_path: str = "app/registry/taxonomy.yaml"
    identity_ontology_path: str = "app/registry/identity_ontology.yaml"

    # ---- HTTP / 禮貌性爬取 ----
    http_timeout_seconds: float = 30.0
    http_max_retries: int = 3
    request_delay_seconds: float = 1.0
    respect_robots_txt: bool = True
    user_agent: str = "BenefitsAI-Crawler/2.0 (+official-source research)"
    ssl_strict_x509: bool = False
    max_items_per_source: int = 300
    # 一層連結追蹤：每個來源最多追幾個同網域連結
    max_followed_links_per_source: int = 120

    # ---- LLM（只支援本地 Ollama）----
    llm_provider: str = "ollama"  # ollama | none
    llm_model: str = "qwen2.5:7b"
    # 資格骨幹抽取用的模型（離線批次，準確度優先；空字串＝沿用 llm_model）。有 5090 可改 qwen3:32b 等較大模型
    core_llm_model: str = "qwen3:8b"
    embedding_model: str = "bge-m3"  # 本地 Ollama embedding 模型（分類的第二個獨立訊號）
    ollama_base_url: str = "http://localhost:11434"
    llm_timeout_seconds: float = 300.0
    llm_max_documents_per_run: int = 500
    llm_assist_matching: bool = True
    llm_min_confidence: float = 0.5
    # 只有分類器分數落在 [low, high) 之間才呼叫 LLM 分類
    classifier_uncertain_low: float = 0.35
    classifier_uncertain_high: float = 0.75

    # ---- 解析規則 ----
    infer_jurisdiction_from_provider: bool = True

    # ---- Matching ----
    match_high_threshold: float = 0.85
    match_possible_threshold: float = 0.5
    # not_match 只能由 confidence >= 此值且非推定的 simple 規則產生
    reject_min_confidence: float = 0.8

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def resolve_path(self, value: str | Path) -> Path:
        path = Path(value)
        return path if path.is_absolute() else (BACKEND_DIR / path).resolve()

    @property
    def data_path(self) -> Path:
        return self.resolve_path(self.data_dir)

    @property
    def raw_storage_path(self) -> Path:
        return self.data_path / "raw"

    @property
    def processed_path(self) -> Path:
        return self.data_path / "processed"

    @property
    def demo_seed_file(self) -> Path:
        return self.resolve_path(self.demo_seed_path)

    @property
    def legacy_seed_file(self) -> Path:
        return self.resolve_path(self.legacy_seed_path)

    @property
    def sources_config_file(self) -> Path:
        return self.resolve_path(self.sources_config_path)

    @property
    def official_domains_file(self) -> Path:
        return self.resolve_path(self.official_domains_path)

    @property
    def keyword_rules_file(self) -> Path:
        path = self.resolve_path(self.keyword_rules_path)
        return path if path.exists() else self.resolve_path(self.keyword_rules_seed_path)

    @property
    def attribute_registry_file(self) -> Path:
        return self.resolve_path(self.attribute_registry_path)

    @property
    def attribute_aliases_mined_file(self) -> Path:
        return self.resolve_path(self.attribute_aliases_mined_path)

    @property
    def taxonomy_file(self) -> Path:
        return self.resolve_path(self.taxonomy_path)

    @property
    def identity_ontology_file(self) -> Path:
        return self.resolve_path(self.identity_ontology_path)


@lru_cache
def get_settings() -> Settings:
    return Settings()
