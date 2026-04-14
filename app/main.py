"""
main.py – Command-line interface for the Solar Panel Management System.

Usage:
    python -m app.main <command> [options]

Commands:
    list-panels                     List all solar panels
    add-panel                       Add a new solar panel (interactive)
    update-status <id> <statut>     Change the statut of a panel
    delete-panel <id>               Delete a panel
    add-production <panel_id>       Record an energy production reading
    list-productions <panel_id>     Show recent production readings
    stats <panel_id>                Show production statistics
    list-alerts                     List unresolved alerts
    add-alert <panel_id>            Create a new alert
    resolve-alert <alert_id>        Mark an alert as resolved
"""

import sys
from datetime import date

from dotenv import load_dotenv
from tabulate import tabulate

from .database import get_connection
from .models import Alerte, Panneau, Production
from .repository import AlerteRepository, PanneauRepository, ProductionRepository

load_dotenv()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _input_float(prompt: str) -> float:
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("  ⚠  Veuillez entrer un nombre valide.")


def _input_choice(prompt: str, choices: tuple) -> str:
    while True:
        value = input(prompt).strip().lower()
        if value in choices:
            return value
        print(f"  ⚠  Choix invalide. Options : {choices}")


# ---------------------------------------------------------------------------
# Panel commands
# ---------------------------------------------------------------------------

def cmd_list_panels() -> None:
    with get_connection() as conn:
        repo = PanneauRepository(conn)
        panels = repo.obtenir_tous()

    if not panels:
        print("Aucun panneau enregistré.")
        return

    rows = [
        [
            p.id,
            p.nom,
            p.localisation,
            f"{p.puissance_kw:.2f} kW",
            p.statut,
            p.date_installation,
        ]
        for p in panels
    ]
    headers = ["ID", "Nom", "Localisation", "Puissance", "Statut", "Installation"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))


def cmd_add_panel() -> None:
    print("=== Ajouter un panneau solaire ===")
    nom = input("Nom          : ").strip()
    localisation = input("Localisation : ").strip()
    puissance = _input_float("Puissance (kW) : ")
    statut = _input_choice(
        "Statut [actif/maintenance/panne] : ", Panneau.STATUTS_VALIDES
    )
    date_str = input("Date d'installation (YYYY-MM-DD, laissez vide pour aujourd'hui) : ").strip()

    installation: date | None = None
    if date_str:
        try:
            installation = date.fromisoformat(date_str)
        except ValueError:
            print("  ⚠  Format de date invalide. On utilise la date d'aujourd'hui.")

    panneau = Panneau(
        nom=nom,
        localisation=localisation,
        puissance_kw=puissance,
        statut=statut,
        date_installation=installation,
    )

    with get_connection() as conn:
        repo = PanneauRepository(conn)
        panneau = repo.creer(panneau)

    print(f"✅ Panneau créé avec l'ID {panneau.id}.")


def cmd_update_status(args: list) -> None:
    if len(args) < 2:
        print("Usage : update-status <id> <statut>")
        sys.exit(1)

    panneau_id = int(args[0])
    statut = args[1].lower()

    with get_connection() as conn:
        repo = PanneauRepository(conn)
        panneau = repo.changer_statut(panneau_id, statut)

    if panneau:
        print(f"✅ Panneau {panneau_id} → statut mis à jour : {panneau.statut}")
    else:
        print(f"❌ Panneau {panneau_id} introuvable.")


def cmd_delete_panel(args: list) -> None:
    if not args:
        print("Usage : delete-panel <id>")
        sys.exit(1)

    panneau_id = int(args[0])
    confirm = input(f"Confirmer la suppression du panneau {panneau_id} ? [o/N] : ").strip().lower()
    if confirm != "o":
        print("Suppression annulée.")
        return

    with get_connection() as conn:
        repo = PanneauRepository(conn)
        deleted = repo.supprimer(panneau_id)

    if deleted:
        print(f"✅ Panneau {panneau_id} supprimé.")
    else:
        print(f"❌ Panneau {panneau_id} introuvable.")


# ---------------------------------------------------------------------------
# Production commands
# ---------------------------------------------------------------------------

def cmd_add_production(args: list) -> None:
    if not args:
        print("Usage : add-production <panel_id>")
        sys.exit(1)

    panneau_id = int(args[0])
    print(f"=== Enregistrer une production pour le panneau {panneau_id} ===")
    energie = _input_float("Énergie produite (kWh) : ")
    temp_str = input("Température (°C, laissez vide si inconnue) : ").strip()
    irr_str = input("Irradiance (W/m², laissez vide si inconnue) : ").strip()

    production = Production(
        panneau_id=panneau_id,
        energie_kwh=energie,
        temperature=float(temp_str) if temp_str else None,
        irradiance=float(irr_str) if irr_str else None,
    )

    with get_connection() as conn:
        repo = ProductionRepository(conn)
        production = repo.enregistrer(production)

    print(f"✅ Production enregistrée avec l'ID {production.id} ({production.horodatage}).")


def cmd_list_productions(args: list) -> None:
    if not args:
        print("Usage : list-productions <panel_id>")
        sys.exit(1)

    panneau_id = int(args[0])

    with get_connection() as conn:
        repo = ProductionRepository(conn)
        productions = repo.obtenir_par_panneau(panneau_id)

    if not productions:
        print(f"Aucune production enregistrée pour le panneau {panneau_id}.")
        return

    rows = [
        [
            p.id,
            f"{p.energie_kwh:.4f} kWh",
            f"{p.temperature:.1f} °C" if p.temperature is not None else "-",
            f"{p.irradiance:.1f} W/m²" if p.irradiance is not None else "-",
            p.horodatage,
        ]
        for p in productions
    ]
    headers = ["ID", "Énergie", "Temp.", "Irradiance", "Horodatage"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))


def cmd_stats(args: list) -> None:
    if not args:
        print("Usage : stats <panel_id>")
        sys.exit(1)

    panneau_id = int(args[0])

    with get_connection() as conn:
        p_repo = PanneauRepository(conn)
        prod_repo = ProductionRepository(conn)
        panneau = p_repo.obtenir_par_id(panneau_id)
        total = prod_repo.production_totale(panneau_id)
        moyenne = prod_repo.production_moyenne(panneau_id)

    if not panneau:
        print(f"❌ Panneau {panneau_id} introuvable.")
        return

    print(f"\n{'=' * 50}")
    print(f"  Statistiques – {panneau.nom}")
    print(f"{'=' * 50}")
    print(f"  Localisation  : {panneau.localisation}")
    print(f"  Puissance     : {panneau.puissance_kw:.2f} kW")
    print(f"  Statut        : {panneau.statut}")
    print(f"  Production totale  : {total:.4f} kWh")
    print(f"  Production moyenne : {moyenne:.4f} kWh / relevé")
    print(f"{'=' * 50}\n")


# ---------------------------------------------------------------------------
# Alert commands
# ---------------------------------------------------------------------------

def cmd_list_alerts() -> None:
    with get_connection() as conn:
        repo = AlerteRepository(conn)
        alertes = repo.obtenir_non_resolues()

    if not alertes:
        print("✅ Aucune alerte non résolue.")
        return

    rows = [
        [a.id, a.panneau_id, a.type_alerte, a.message[:60], a.horodatage]
        for a in alertes
    ]
    headers = ["ID", "Panneau", "Type", "Message", "Horodatage"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))


def cmd_add_alert(args: list) -> None:
    if not args:
        print("Usage : add-alert <panel_id>")
        sys.exit(1)

    panneau_id = int(args[0])
    print(f"=== Créer une alerte pour le panneau {panneau_id} ===")
    type_alerte = _input_choice(
        "Type [surchauffe/sous-production/panne/maintenance] : ",
        Alerte.TYPES_VALIDES,
    )
    message = input("Message : ").strip()

    alerte = Alerte(panneau_id=panneau_id, type_alerte=type_alerte, message=message)

    with get_connection() as conn:
        repo = AlerteRepository(conn)
        alerte = repo.creer(alerte)

    print(f"✅ Alerte créée avec l'ID {alerte.id}.")


def cmd_resolve_alert(args: list) -> None:
    if not args:
        print("Usage : resolve-alert <alert_id>")
        sys.exit(1)

    alerte_id = int(args[0])

    with get_connection() as conn:
        repo = AlerteRepository(conn)
        resolved = repo.resoudre(alerte_id)

    if resolved:
        print(f"✅ Alerte {alerte_id} marquée comme résolue.")
    else:
        print(f"❌ Alerte {alerte_id} introuvable.")


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

COMMANDS = {
    "list-panels":      (cmd_list_panels,      []),
    "add-panel":        (cmd_add_panel,         []),
    "update-status":    (cmd_update_status,     ["<id>", "<statut>"]),
    "delete-panel":     (cmd_delete_panel,      ["<id>"]),
    "add-production":   (cmd_add_production,    ["<panel_id>"]),
    "list-productions": (cmd_list_productions,  ["<panel_id>"]),
    "stats":            (cmd_stats,             ["<panel_id>"]),
    "list-alerts":      (cmd_list_alerts,       []),
    "add-alert":        (cmd_add_alert,         ["<panel_id>"]),
    "resolve-alert":    (cmd_resolve_alert,     ["<alert_id>"]),
}


def print_help() -> None:
    print("Panneau Solaire – Gestion des panneaux solaires\n")
    print("Usage : python -m app.main <commande> [options]\n")
    print("Commandes disponibles :")
    for name, (_, params) in COMMANDS.items():
        print(f"  {name} {' '.join(params)}")


def main() -> None:
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_help()
        return

    command = sys.argv[1]
    rest = sys.argv[2:]

    if command not in COMMANDS:
        print(f"Commande inconnue : '{command}'. Utilisez --help pour la liste.")
        sys.exit(1)

    func, _ = COMMANDS[command]
    try:
        if rest:
            func(rest)
        else:
            func()
    except ValueError as exc:
        print(f"❌ Erreur de validation : {exc}")
        sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        print(f"❌ Erreur ({type(exc).__name__}) : {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
