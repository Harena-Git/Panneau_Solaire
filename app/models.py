"""
models.py – Plain data classes (no ORM) representing database entities.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Optional


@dataclass
class Panneau:
    """Represents a solar panel (table: panneaux)."""

    nom: str
    localisation: str
    puissance_kw: float
    statut: str = "actif"
    date_installation: Optional[date] = None
    id: Optional[int] = None
    date_creation: Optional[datetime] = None
    date_modification: Optional[datetime] = None

    STATUTS_VALIDES = ("actif", "maintenance", "panne")

    def valider(self) -> None:
        """Raise ValueError if the object contains invalid data."""
        if not self.nom or not self.nom.strip():
            raise ValueError("Le nom du panneau ne peut pas être vide.")
        if not self.localisation or not self.localisation.strip():
            raise ValueError("La localisation ne peut pas être vide.")
        if self.puissance_kw <= 0:
            raise ValueError("La puissance doit être un nombre positif.")
        if self.statut not in self.STATUTS_VALIDES:
            raise ValueError(
                f"Statut invalide '{self.statut}'. "
                f"Valeurs acceptées : {self.STATUTS_VALIDES}"
            )


@dataclass
class Production:
    """Represents an energy-production reading (table: productions)."""

    panneau_id: int
    energie_kwh: float
    temperature: Optional[float] = None
    irradiance: Optional[float] = None
    horodatage: Optional[datetime] = None
    id: Optional[int] = None

    def valider(self) -> None:
        if self.energie_kwh < 0:
            raise ValueError("L'énergie produite ne peut pas être négative.")


@dataclass
class Alerte:
    """Represents an alert / anomaly (table: alertes)."""

    panneau_id: int
    type_alerte: str
    message: str
    resolue: bool = False
    horodatage: Optional[datetime] = None
    id: Optional[int] = None

    TYPES_VALIDES = ("surchauffe", "sous-production", "panne", "maintenance")

    def valider(self) -> None:
        if self.type_alerte not in self.TYPES_VALIDES:
            raise ValueError(
                f"Type d'alerte invalide '{self.type_alerte}'. "
                f"Valeurs acceptées : {self.TYPES_VALIDES}"
            )
        if not self.message or not self.message.strip():
            raise ValueError("Le message de l'alerte ne peut pas être vide.")
