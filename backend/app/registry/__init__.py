"""屬性登錄表、領域類別樹、身分本體（YAML 資料 → 記憶體物件 → MongoDB 同步）。"""

from .loader import Attribute, Registry, TaxonomyNode, IdentityTag, get_registry, reset_registry

__all__ = ["Attribute", "Registry", "TaxonomyNode", "IdentityTag", "get_registry", "reset_registry"]
