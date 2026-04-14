"""
Unit tests for models.py – validation logic only (no database required).
"""

import pytest
from datetime import date

from app.models import Alerte, Panneau, Production


# ---------------------------------------------------------------------------
# Panneau
# ---------------------------------------------------------------------------

class TestPanneauValidation:
    def test_valid_panel_passes(self):
        p = Panneau(nom="Test", localisation="Toit", puissance_kw=5.0)
        p.valider()  # should not raise

    def test_empty_nom_raises(self):
        p = Panneau(nom="", localisation="Toit", puissance_kw=5.0)
        with pytest.raises(ValueError, match="nom"):
            p.valider()

    def test_blank_nom_raises(self):
        p = Panneau(nom="   ", localisation="Toit", puissance_kw=5.0)
        with pytest.raises(ValueError, match="nom"):
            p.valider()

    def test_empty_localisation_raises(self):
        p = Panneau(nom="Test", localisation="", puissance_kw=5.0)
        with pytest.raises(ValueError, match="localisation"):
            p.valider()

    def test_zero_puissance_raises(self):
        p = Panneau(nom="Test", localisation="Toit", puissance_kw=0.0)
        with pytest.raises(ValueError, match="puissance"):
            p.valider()

    def test_negative_puissance_raises(self):
        p = Panneau(nom="Test", localisation="Toit", puissance_kw=-1.0)
        with pytest.raises(ValueError, match="puissance"):
            p.valider()

    def test_invalid_statut_raises(self):
        p = Panneau(nom="Test", localisation="Toit", puissance_kw=5.0, statut="inconnu")
        with pytest.raises(ValueError, match="Statut"):
            p.valider()

    @pytest.mark.parametrize("statut", Panneau.STATUTS_VALIDES)
    def test_valid_statuts(self, statut):
        p = Panneau(nom="Test", localisation="Toit", puissance_kw=5.0, statut=statut)
        p.valider()  # should not raise


# ---------------------------------------------------------------------------
# Production
# ---------------------------------------------------------------------------

class TestProductionValidation:
    def test_valid_production_passes(self):
        p = Production(panneau_id=1, energie_kwh=4.5)
        p.valider()

    def test_zero_energie_passes(self):
        # 0 kWh is a valid reading (e.g., at night)
        p = Production(panneau_id=1, energie_kwh=0.0)
        p.valider()

    def test_negative_energie_raises(self):
        p = Production(panneau_id=1, energie_kwh=-1.0)
        with pytest.raises(ValueError, match="négative"):
            p.valider()


# ---------------------------------------------------------------------------
# Alerte
# ---------------------------------------------------------------------------

class TestAlerteValidation:
    def test_valid_alerte_passes(self):
        a = Alerte(panneau_id=1, type_alerte="panne", message="Court-circuit détecté")
        a.valider()

    def test_invalid_type_raises(self):
        a = Alerte(panneau_id=1, type_alerte="inconnu", message="Problème")
        with pytest.raises(ValueError, match="Type"):
            a.valider()

    def test_empty_message_raises(self):
        a = Alerte(panneau_id=1, type_alerte="panne", message="")
        with pytest.raises(ValueError, match="message"):
            a.valider()

    def test_blank_message_raises(self):
        a = Alerte(panneau_id=1, type_alerte="panne", message="   ")
        with pytest.raises(ValueError, match="message"):
            a.valider()

    @pytest.mark.parametrize("type_alerte", Alerte.TYPES_VALIDES)
    def test_valid_types(self, type_alerte):
        a = Alerte(panneau_id=1, type_alerte=type_alerte, message="Test")
        a.valider()
