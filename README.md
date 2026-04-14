# Panneau Solaire 🌞

Système de gestion de panneaux solaires — **Python · SQL Server · Docker**

> Projet de Rattrapage Programmation S4

---

## Architecture

```
Panneau_Solaire/
├── app/
│   ├── __init__.py       # Package Python
│   ├── database.py       # Connexion SQL Server (pyodbc)
│   ├── models.py         # Modèles de données (Panneau, Production, Alerte)
│   ├── repository.py     # Opérations CRUD
│   └── main.py           # Interface en ligne de commande (CLI)
├── sql/
│   └── init.sql          # Schéma + données d'exemple
├── tests/
│   ├── test_models.py    # Tests unitaires des modèles
│   └── test_repository.py# Tests des repositories
├── docker-compose.yml    # Orchestration des services
├── Dockerfile            # Image de l'application Python
├── requirements.txt      # Dépendances Python
└── .env.example          # Variables d'environnement (modèle)
```

### Services Docker

| Service      | Description                                  | Port  |
|-------------|----------------------------------------------|-------|
| `sqlserver` | Microsoft SQL Server 2022 Express            | 1433  |
| `db-init`   | Initialisation du schéma (exécution unique)  | —     |
| `app`       | Application Python (CLI)                     | —     |

---

## Prérequis

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) ≥ 24
- [Docker Compose](https://docs.docker.com/compose/) (inclus avec Docker Desktop)

---

## Démarrage rapide

### 1 — Copier le fichier de configuration

```bash
cp .env.example .env
# Modifier SA_PASSWORD si nécessaire (doit respecter la complexité SQL Server)
```

### 2 — Démarrer les services

```bash
docker-compose up -d sqlserver
# Attendre ~30 secondes que SQL Server soit prêt, puis :
docker-compose up db-init
```

### 3 — Utiliser l'application

```bash
# Afficher l'aide
docker-compose run --rm app

# Lister tous les panneaux
docker-compose run --rm app python -m app.main list-panels

# Ajouter un panneau (interactif)
docker-compose run --rm app python -m app.main add-panel

# Changer le statut d'un panneau
docker-compose run --rm app python -m app.main update-status 1 maintenance

# Enregistrer une production (interactif)
docker-compose run --rm app python -m app.main add-production 1

# Voir les productions d'un panneau
docker-compose run --rm app python -m app.main list-productions 1

# Statistiques de production
docker-compose run --rm app python -m app.main stats 1

# Lister les alertes non résolues
docker-compose run --rm app python -m app.main list-alerts

# Créer une alerte (interactif)
docker-compose run --rm app python -m app.main add-alert 1

# Résoudre une alerte
docker-compose run --rm app python -m app.main resolve-alert 1
```

---

## Développement local

### Prérequis supplémentaires

- Python 3.11+
- [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Installation

```bash
python -m venv .venv
source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install -r requirements.txt
pip install pytest           # pour les tests
```

### Variables d'environnement

Créer un fichier `.env` (voir `.env.example`) ou exporter les variables :

```bash
export DB_SERVER=localhost
export DB_PORT=1433
export DB_NAME=PanneauSolaire
export DB_USER=sa
export DB_PASSWORD=PanneauSolaire2024!
```

### Exécuter les tests

Les tests unitaires ne nécessitent **pas** de SQL Server :

```bash
pytest tests/ -v
```

---

## Schéma de la base de données

```
panneaux
├── id               INT  PK IDENTITY
├── nom              NVARCHAR(100)
├── localisation     NVARCHAR(255)
├── puissance_kw     DECIMAL(10,2)
├── statut           NVARCHAR(20)  [actif | maintenance | panne]
├── date_installation DATE
├── date_creation    DATETIME2
└── date_modification DATETIME2

productions
├── id               INT  PK IDENTITY
├── panneau_id       INT  FK → panneaux(id)
├── energie_kwh      DECIMAL(10,4)
├── temperature      DECIMAL(5,2)   (nullable)
├── irradiance       DECIMAL(8,2)   (nullable)
└── horodatage       DATETIME2

alertes
├── id               INT  PK IDENTITY
├── panneau_id       INT  FK → panneaux(id)
├── type_alerte      NVARCHAR(50)  [surchauffe | sous-production | panne | maintenance]
├── message          NVARCHAR(500)
├── resolue          BIT
└── horodatage       DATETIME2
```

---

## Technologies utilisées

| Technologie | Rôle |
|---|---|
| Python 3.12 | Logique applicative & CLI |
| pyodbc | Connecteur SQL Server |
| python-dotenv | Gestion des variables d'environnement |
| tabulate | Affichage des tableaux en CLI |
| SQL Server 2022 | Persistance des données |
| Docker / Compose | Conteneurisation & orchestration |
