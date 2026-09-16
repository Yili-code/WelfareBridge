"""REST API routers（全部掛在 /api 底下）。"""

from . import admin, assistant, benefits, diagnostics, matching, meta, public

ROUTERS = [admin.router, meta.router, benefits.router, matching.router, assistant.router, diagnostics.router, public.router]

__all__ = ["ROUTERS"]
