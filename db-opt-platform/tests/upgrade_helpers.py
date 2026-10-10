"""Shared helpers for the Final Upgrade tests (new file; the pre-existing conftest is not modified)."""
from __future__ import annotations

import asyncio

import pytest

from tests.conftest import live_db_available  # noqa: F401  (also sets test env defaults)


def admin_db_available() -> bool:
    try:
        import psycopg2
        from app.config import get_settings
        st = get_settings()
        c = psycopg2.connect(**{k if k != "database" else "dbname": v for k, v in st.admin_dsn_kwargs.items()},
                             connect_timeout=2)
        c.close()
        return True
    except Exception:  # noqa: BLE001
        return False


requires_admin_db = pytest.mark.skipif(not admin_db_available(), reason="admin PostgreSQL not reachable (NOT RUN)")


def admin_exec(sql: str, *args):
    import psycopg2
    from app.config import get_settings
    st = get_settings()
    c = psycopg2.connect(**{k if k != "database" else "dbname": v for k, v in st.admin_dsn_kwargs.items()})
    c.autocommit = True
    try:
        with c.cursor() as cur:
            cur.execute(sql, args or None)
            try:
                return cur.fetchall()
            except psycopg2.ProgrammingError:
                return None
    finally:
        c.close()


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro) if False else asyncio.run(coro)
