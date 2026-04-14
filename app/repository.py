"""
repository.py – CRUD operations for the three main entities.

Each repository class takes a pyodbc.Connection in its constructor so that
connection management (and test injection) stays outside the data layer.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

import pyodbc

from .models import Alerte, Panneau, Production


# ---------------------------------------------------------------------------
# PanneauRepository
# ---------------------------------------------------------------------------

class PanneauRepository:
    """CRUD operations for the *panneaux* table."""

    def __init__(self, conn: pyodbc.Connection) -> None:
        self._conn = conn

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def creer(self, panneau: Panneau) -> Panneau:
        """Insert a new panel and return it with its generated id."""
        panneau.valider()
        installation = panneau.date_installation or date.today()

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO panneaux (nom, localisation, puissance_kw, statut, date_installation)
            OUTPUT INSERTED.id, INSERTED.date_creation, INSERTED.date_modification
            VALUES (?, ?, ?, ?, ?)
            """,
            panneau.nom,
            panneau.localisation,
            panneau.puissance_kw,
            panneau.statut,
            installation,
        )
        row = cursor.fetchone()
        self._conn.commit()

        panneau.id = row[0]
        panneau.date_creation = row[1]
        panneau.date_modification = row[2]
        panneau.date_installation = installation
        return panneau

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------
    def obtenir_tous(self) -> List[Panneau]:
        """Return all panels ordered by id."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, nom, localisation, puissance_kw, statut, "
            "date_installation, date_creation, date_modification "
            "FROM panneaux ORDER BY id"
        )
        return [self._row_to_panneau(r) for r in cursor.fetchall()]

    def obtenir_par_id(self, panneau_id: int) -> Optional[Panneau]:
        """Return a single panel or None if not found."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, nom, localisation, puissance_kw, statut, "
            "date_installation, date_creation, date_modification "
            "FROM panneaux WHERE id = ?",
            panneau_id,
        )
        row = cursor.fetchone()
        return self._row_to_panneau(row) if row else None

    def obtenir_par_statut(self, statut: str) -> List[Panneau]:
        """Return panels filtered by statut."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, nom, localisation, puissance_kw, statut, "
            "date_installation, date_creation, date_modification "
            "FROM panneaux WHERE statut = ? ORDER BY id",
            statut,
        )
        return [self._row_to_panneau(r) for r in cursor.fetchall()]

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------
    def mettre_a_jour(self, panneau: Panneau) -> Panneau:
        """Update an existing panel."""
        if panneau.id is None:
            raise ValueError("L'id du panneau est requis pour la mise à jour.")
        panneau.valider()

        cursor = self._conn.cursor()
        cursor.execute(
            """
            UPDATE panneaux
            SET nom = ?, localisation = ?, puissance_kw = ?,
                statut = ?, date_modification = GETDATE()
            WHERE id = ?
            """,
            panneau.nom,
            panneau.localisation,
            panneau.puissance_kw,
            panneau.statut,
            panneau.id,
        )
        self._conn.commit()
        return self.obtenir_par_id(panneau.id)

    def changer_statut(self, panneau_id: int, statut: str) -> Optional[Panneau]:
        """Change only the statut of a panel."""
        if statut not in Panneau.STATUTS_VALIDES:
            raise ValueError(f"Statut invalide : {statut}")

        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE panneaux SET statut = ?, date_modification = GETDATE() WHERE id = ?",
            statut,
            panneau_id,
        )
        self._conn.commit()
        return self.obtenir_par_id(panneau_id)

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------
    def supprimer(self, panneau_id: int) -> bool:
        """Delete a panel; returns True if a row was deleted."""
        cursor = self._conn.cursor()
        cursor.execute("DELETE FROM panneaux WHERE id = ?", panneau_id)
        affected = cursor.rowcount
        self._conn.commit()
        return affected > 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _row_to_panneau(row) -> Panneau:
        return Panneau(
            id=row[0],
            nom=row[1],
            localisation=row[2],
            puissance_kw=float(row[3]),
            statut=row[4],
            date_installation=row[5],
            date_creation=row[6],
            date_modification=row[7],
        )


# ---------------------------------------------------------------------------
# ProductionRepository
# ---------------------------------------------------------------------------

class ProductionRepository:
    """CRUD operations for the *productions* table."""

    def __init__(self, conn: pyodbc.Connection) -> None:
        self._conn = conn

    def enregistrer(self, production: Production) -> Production:
        """Insert a production reading and return it with its generated id."""
        production.valider()

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO productions (panneau_id, energie_kwh, temperature, irradiance, horodatage)
            OUTPUT INSERTED.id, INSERTED.horodatage
            VALUES (?, ?, ?, ?, COALESCE(?, GETDATE()))
            """,
            production.panneau_id,
            production.energie_kwh,
            production.temperature,
            production.irradiance,
            production.horodatage,
        )
        row = cursor.fetchone()
        self._conn.commit()

        production.id = row[0]
        production.horodatage = row[1]
        return production

    def obtenir_par_panneau(self, panneau_id: int, limite: int = 100) -> List[Production]:
        """Return the last *limite* readings for a given panel."""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT TOP (?) id, panneau_id, energie_kwh, temperature, irradiance, horodatage
            FROM productions
            WHERE panneau_id = ?
            ORDER BY horodatage DESC
            """,
            limite,
            panneau_id,
        )
        return [self._row_to_production(r) for r in cursor.fetchall()]

    def production_totale(self, panneau_id: int) -> float:
        """Return the sum of all energy readings for a panel (kWh)."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT COALESCE(SUM(energie_kwh), 0) FROM productions WHERE panneau_id = ?",
            panneau_id,
        )
        return float(cursor.fetchone()[0])

    def production_moyenne(self, panneau_id: int) -> float:
        """Return the average energy reading for a panel (kWh)."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT COALESCE(AVG(energie_kwh), 0) FROM productions WHERE panneau_id = ?",
            panneau_id,
        )
        return float(cursor.fetchone()[0])

    @staticmethod
    def _row_to_production(row) -> Production:
        return Production(
            id=row[0],
            panneau_id=row[1],
            energie_kwh=float(row[2]),
            temperature=float(row[3]) if row[3] is not None else None,
            irradiance=float(row[4]) if row[4] is not None else None,
            horodatage=row[5],
        )


# ---------------------------------------------------------------------------
# AlerteRepository
# ---------------------------------------------------------------------------

class AlerteRepository:
    """CRUD operations for the *alertes* table."""

    def __init__(self, conn: pyodbc.Connection) -> None:
        self._conn = conn

    def creer(self, alerte: Alerte) -> Alerte:
        """Insert a new alert and return it with its generated id."""
        alerte.valider()

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT INTO alertes (panneau_id, type_alerte, message, resolue, horodatage)
            OUTPUT INSERTED.id, INSERTED.horodatage
            VALUES (?, ?, ?, ?, COALESCE(?, GETDATE()))
            """,
            alerte.panneau_id,
            alerte.type_alerte,
            alerte.message,
            1 if alerte.resolue else 0,
            alerte.horodatage,
        )
        row = cursor.fetchone()
        self._conn.commit()

        alerte.id = row[0]
        alerte.horodatage = row[1]
        return alerte

    def obtenir_non_resolues(self) -> List[Alerte]:
        """Return all open (unresolved) alerts."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, panneau_id, type_alerte, message, resolue, horodatage "
            "FROM alertes WHERE resolue = 0 ORDER BY horodatage DESC"
        )
        return [self._row_to_alerte(r) for r in cursor.fetchall()]

    def obtenir_par_panneau(self, panneau_id: int) -> List[Alerte]:
        """Return all alerts for a given panel."""
        cursor = self._conn.cursor()
        cursor.execute(
            "SELECT id, panneau_id, type_alerte, message, resolue, horodatage "
            "FROM alertes WHERE panneau_id = ? ORDER BY horodatage DESC",
            panneau_id,
        )
        return [self._row_to_alerte(r) for r in cursor.fetchall()]

    def resoudre(self, alerte_id: int) -> bool:
        """Mark an alert as resolved; returns True if a row was updated."""
        cursor = self._conn.cursor()
        cursor.execute(
            "UPDATE alertes SET resolue = 1 WHERE id = ?",
            alerte_id,
        )
        affected = cursor.rowcount
        self._conn.commit()
        return affected > 0

    @staticmethod
    def _row_to_alerte(row) -> Alerte:
        return Alerte(
            id=row[0],
            panneau_id=row[1],
            type_alerte=row[2],
            message=row[3],
            resolue=bool(row[4]),
            horodatage=row[5],
        )
