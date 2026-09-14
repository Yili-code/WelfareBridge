"""REST API routers（全部掛在 /api 底下）。"""

from . import admin, assistant, benefits, diagnostics, matching, meta

ROUTERS = [admin.router, meta.router, benefits.router, matching.router, assistant.router, diagnostics.router]

__all__ = ["ROUTERS"]
