"""REST API routers（全部掛在 /api 底下）。"""

from . import admin, benefits, matching, meta

ROUTERS = [admin.router, meta.router, benefits.router, matching.router]

__all__ = ["ROUTERS"]
