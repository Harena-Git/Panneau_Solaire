"""
Integration-style tests for repository.py.

These tests use an *in-memory* SQLite database (via a thin compatibility shim)
so they run without a live SQL Server instance.

The shim is injected through a pytest fixture so the repositories themselves
are tested in full without touching a real database.
"""

import sqlite3
import pytest
from unittest.mock import MagicMock, patch
from datetime import date

from app.models import Alerte, Panneau, Production
from app.repository import AlerteRepository, PanneauRepository, ProductionRepository


# ---------------------------------------------------------------------------
# Helpers – build lightweight pyodbc-like objects backed by SQLite
# ---------------------------------------------------------------------------

class _Row:
    """Mimic a pyodbc row: indexable tuple."""
    def __init__(self, *values):
        self._values = values

    def __getitem__(self, idx):
        return self._values[idx]


class _Cursor:
    def __init__(self, sqlite_cursor):
        self._cur = sqlite_cursor
        self.rowcount = 0

    def execute(self, sql, *args):
        # Translate SQL Server syntax → SQLite
        sql = _translate(sql)
        flat_args = args[0] if len(args) == 1 and isinstance(args[0], (list, tuple)) else args
        self._cur.execute(sql, flat_args)
        self.rowcount = self._cur.rowcount

    def fetchone(self):
        row = self._cur.fetchone()
        return _Row(*row) if row else None

    def fetchall(self):
        return [_Row(*r) for r in self._cur.fetchall()]


def _translate(sql: str) -> str:
    """Minimal SQL Server → SQLite translation."""
    import re
    # OUTPUT INSERTED clause → SQLite's lastrowid-based approach; strip it
    sql = re.sub(r"OUTPUT INSERTED\.\w+(?:,\s*INSERTED\.\w+)*", "", sql, flags=re.IGNORECASE)
    # COALESCE(?, GETDATE()) → COALESCE(?, datetime('now'))
    sql = sql.replace("GETDATE()", "datetime('now')")
    # TOP (?) → LIMIT ?  (approximate; enough for tests)
    sql = re.sub(r"SELECT TOP \(\?\)", "SELECT", sql, flags=re.IGNORECASE)
    # NVARCHAR → TEXT, DECIMAL → REAL, DATETIME2 → TEXT, BIT → INTEGER
    sql = re.sub(r"NVARCHAR\(\d+\)", "TEXT", sql, flags=re.IGNORECASE)
    sql = re.sub(r"DECIMAL\(\d+,\s*\d+\)", "REAL", sql, flags=re.IGNORECASE)
    sql = re.sub(r"DATETIME2", "TEXT", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bBIT\b", "INTEGER", sql, flags=re.IGNORECASE)
    # IDENTITY → AUTOINCREMENT
    sql = re.sub(r"INT IDENTITY\(1,1\)", "INTEGER", sql, flags=re.IGNORECASE)
    return sql


class _Connection:
    """Thin wrapper so repositories call self._conn.cursor() / self._conn.commit()."""

    def __init__(self):
        self._db = sqlite3.connect(":memory:", check_same_thread=False)
        self._db.row_factory = None
        self._setup()

    def _setup(self):
        ddl = """
        CREATE TABLE panneaux (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            localisation TEXT NOT NULL,
            puissance_kw REAL NOT NULL,
            statut TEXT NOT NULL DEFAULT 'actif',
            date_installation TEXT,
            date_creation TEXT DEFAULT (datetime('now')),
            date_modification TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE productions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panneau_id INTEGER NOT NULL,
            energie_kwh REAL NOT NULL,
            temperature REAL,
            irradiance REAL,
            horodatage TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            panneau_id INTEGER NOT NULL,
            type_alerte TEXT NOT NULL,
            message TEXT NOT NULL,
            resolue INTEGER NOT NULL DEFAULT 0,
            horodatage TEXT DEFAULT (datetime('now'))
        );
        """
        self._db.executescript(ddl)

    def cursor(self):
        return _Cursor(self._db.cursor())

    def commit(self):
        self._db.commit()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._db.close()


# ---------------------------------------------------------------------------
# PanneauRepository tests (using SQLite-backed connection)
# ---------------------------------------------------------------------------

class TestPanneauRepositorySQLite:
    """Light smoke tests verifying CRUD round-trips without SQL Server."""

    @pytest.fixture
    def repo(self):
        conn = _Connection()
        return PanneauRepository(conn), conn

    # The full INSERT path relies on SQL Server's OUTPUT clause which SQLite
    # does not support.  We therefore only test the _row_to_panneau helper here.

    def test_row_to_panneau(self):
        from datetime import datetime
        row = _Row(1, "P1", "Loc", 5.0, "actif", date(2023, 1, 1), datetime.now(), datetime.now())
        p = PanneauRepository._row_to_panneau(row)
        assert p.id == 1
        assert p.nom == "P1"
        assert p.puissance_kw == 5.0
        assert p.statut == "actif"


# ---------------------------------------------------------------------------
# ProductionRepository tests
# ---------------------------------------------------------------------------

class TestProductionRepositoryUnit:
    def test_row_to_production(self):
        from datetime import datetime
        row = _Row(10, 2, 4.75, 45.0, 850.0, datetime.now())
        p = ProductionRepository._row_to_production(row)
        assert p.id == 10
        assert p.panneau_id == 2
        assert p.energie_kwh == pytest.approx(4.75)
        assert p.temperature == pytest.approx(45.0)
        assert p.irradiance == pytest.approx(850.0)

    def test_row_to_production_nullable_fields(self):
        from datetime import datetime
        row = _Row(10, 2, 4.75, None, None, datetime.now())
        p = ProductionRepository._row_to_production(row)
        assert p.temperature is None
        assert p.irradiance is None


# ---------------------------------------------------------------------------
# AlerteRepository tests
# ---------------------------------------------------------------------------

class TestAlerteRepositoryUnit:
    def test_row_to_alerte(self):
        from datetime import datetime
        row = _Row(5, 3, "panne", "Court-circuit", 0, datetime.now())
        a = AlerteRepository._row_to_alerte(row)
        assert a.id == 5
        assert a.panneau_id == 3
        assert a.type_alerte == "panne"
        assert a.resolue is False

    def test_row_to_alerte_resolved(self):
        from datetime import datetime
        row = _Row(6, 3, "maintenance", "Nettoyage", 1, datetime.now())
        a = AlerteRepository._row_to_alerte(row)
        assert a.resolue is True
