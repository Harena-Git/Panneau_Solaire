## 🎯 Objectif du projet

Développer un système (Python + SQL Server) capable de :

* Permettre à l’utilisateur de saisir ses appareils électriques
* Calculer la **consommation énergétique quotidienne**
* Déterminer :

  * la **puissance nécessaire des panneaux solaires (W)**
  * la **capacité nécessaire de la batterie (Wh / kWh)**
* Optimiser l'utilisation entre :

  * énergie solaire (jour)
  * batterie (nuit)

---

# 🔁 🔥 Fonctionnalité principale : INPUT → CALCUL → OUTPUT

## 📥 INPUT (Entrée utilisateur)

L’utilisateur saisit une liste d’appareils avec :

* nom
* puissance (W)
* durée d’utilisation (heures)
* tranche horaire

### Exemple :

```json
[
  {
    "nom": "Télévision",
    "puissance_w": 75,
    "duree_h": 1,
    "tranche": "matin"
  },
  {
    "nom": "Ordinateur",
    "puissance_w": 150,
    "duree_h": 2,
    "tranche": "nuit"
  },
  {
    "nom": "Lumière",
    "puissance_w": 50,
    "duree_h": 1,
    "tranche": "nuit"
  }
]
```

---

## ⚙️ TRAITEMENT (Pipeline de calcul)

### 1. Calcul énergie par appareil

```python
energie = puissance_w * duree_h
```

---

### 2. Séparation jour / nuit

```python
if tranche in ["matin", "apres-midi"]:
    energie_jour += energie
else:
    energie_nuit += energie
```

---

### 3. Calcul batterie nécessaire

```python
batterie = energie_nuit * 1.5
```

---

### 4. Calcul besoin total panneau

```python
besoin_total = energie_jour + energie_nuit
```

---

### 5. Calcul puissance panneau réel

```python
puissance_panneau = besoin_total / (heures_soleil * 0.4)
```

---

## 📤 OUTPUT (Résultat du système)

Le système retourne :

```json
{
  "energie_jour_wh": 225,
  "energie_nuit_wh": 200,
  "batterie_recommandee_wh": 300,
  "puissance_panneau_recommandee_w": 500
}
```

---

# ⚙️ Règles métier

## 🔌 1. Consommation des appareils

```text
Energie (Wh) = Puissance (W) × Durée (h)
```

---

## 🕒 2. Tranches horaires

| Tranche        | Heure     | Source principale |
| -------------- | --------- | ----------------- |
| Matin          | 06h → 17h | Panneau solaire   |
| Fin de journée | 17h → 19h | Panneau (50%)     |
| Nuit           | 19h → 06h | Batterie          |

---

## ☀️ 3. Production panneaux

* 40% de rendement réel

```text
Puissance réelle = Puissance panneau × 0.4
```

* 50% entre 17h et 19h

---

## 🔋 4. Batterie

* Stockage en Wh / kWh
* Marge de sécurité : +50%

```text
Capacité batterie = besoin_nuit × 1.5
```

---

## 🔄 5. Recharge batterie

* Pendant la journée :

  * alimente les appareils
  * recharge la batterie

👉 Contrainte :

```text
Batterie = 100% à 17h
```

---

## ⏱️ 6. Temps de charge

```text
Temps (h) = Capacité batterie / Puissance disponible
```

---

# 🧠 Logique globale

### Étape 1 : Séparer les consommations

* Jour
* Nuit

---

### Étape 2 : Calcul énergie

```text
Energie jour = somme appareils jour
Energie nuit = somme appareils nuit
```

---

### Étape 3 : Batterie

```text
Batterie = Energie nuit × 1.5
```

---

### Étape 4 : Panneaux

```text
Besoin total = Energie jour + Energie nuit
Puissance panneau = Besoin / (heures × 0.4)
```

---

# 🧩 Architecture du projet

## 📦 Modules Python

---

### 1. `models/`

#### `Appareil`

```python
- id
- nom
- puissance_w
- duree_h
- tranche
```

---

### 2. `database/`

* Connexion SQL Server
* CRUD appareils

Tables :

```text
Appareils
Consommations
Resultats
```

---

### 3. `services/`

#### `consommation_service.py`

* calcul énergie appareil
* total jour / nuit

---

#### `batterie_service.py`

* calcul batterie

---

#### `panneau_service.py`

* calcul panneau

---

#### 🔥 `systeme_dimensionnement.py` (NOUVEAU — MODULE PRINCIPAL)

👉 Gère tout le flux :

### Fonction principale :

```python
def calculer_systeme(appareils: list):
    energie_jour = 0
    energie_nuit = 0

    for app in appareils:
        energie = app["puissance_w"] * app["duree_h"]

        if app["tranche"] in ["matin", "apres-midi"]:
            energie_jour += energie
        else:
            energie_nuit += energie

    batterie = energie_nuit * 1.5
    besoin_total = energie_jour + energie_nuit

    heures_soleil = 11
    puissance_panneau = besoin_total / (heures_soleil * 0.4)

    return {
        "energie_jour": energie_jour,
        "energie_nuit": energie_nuit,
        "batterie": batterie,
        "panneau": puissance_panneau
    }
```

---

### 4. `utils/`

* conversions unités
* helpers

---

# 🗄️ Base de données

## Table : `appareils`

```sql
id INT PRIMARY KEY IDENTITY
nom VARCHAR(100)
puissance_w FLOAT
duree_h FLOAT
tranche VARCHAR(20)
```

---

## Table : `resultats`

```sql
id INT PRIMARY KEY IDENTITY
energie_jour FLOAT
energie_nuit FLOAT
batterie_wh FLOAT
panneau_w FLOAT
date_calcul DATETIME
```

---

# 🖥️ Interface utilisateur

## CLI (terminal)

```python
appareils = []

while True:
    nom = input("Nom appareil : ")
    puissance = float(input("Puissance (W) : "))
    duree = float(input("Durée (h) : "))
    tranche = input("Tranche (matin / apres-midi / nuit) : ")

    appareils.append({
        "nom": nom,
        "puissance_w": puissance,
        "duree_h": duree,
        "tranche": tranche
    })

    stop = input("Ajouter autre ? (n pour stop) : ")
    if stop == "n":
        break
```

---

## Affichage résultats

```python
resultat = calculer_systeme(appareils)

print("Energie jour :", resultat["energie_jour"], "Wh")
print("Energie nuit :", resultat["energie_nuit"], "Wh")
print("Batterie recommandée :", resultat["batterie"], "Wh")
print("Panneau recommandé :", resultat["panneau"], "W")
```

---

# ✅ TODO

## Phase 1

* [ ] Base SQL Server
* [ ] Tables
* [ ] Connexion Python

---

## Phase 2

* [ ] Calcul énergie
* [ ] Jour / nuit
* [ ] Batterie
* [ ] Panneaux

---

## Phase 3

* [ ] Module `systeme_dimensionnement`
* [ ] Simulation complète

---

## Phase 4

* [ ] Interface CLI
* [ ] Interface GUI / Web

---

## Phase 5

* [ ] Historique
* [ ] Export
* [ ] Optimisation rendement

---

# 🚀 Résultat attendu

Le système doit fournir :

* 🔋 Batterie recommandée
* ☀️ Panneaux nécessaires
* 📊 Détail consommation

---
