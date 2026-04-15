## 🎯 Objectif du projet

Développer un système (Python + SQL Server) capable de :

* Calculer la **consation énergétique quotidienne**
* Déterminer :

  * la **puissance nécessaire des panneaux solaires (W)**
  * la **capacité nécessaire de la batterie (Wh / kWh)**
* Optimiser l'utilisation entre :

  * énergie solaire (jour)
  * batterie (nuit)

---

## ⚙️ Règles métier (logique du système)

### 🔌 1. Consommation des appareils

Chaque appareil possède :

* un **nom**
* une **puissance (W)**
* une **durée d’utilisation (heures)**
* une **tranche horaire**

👉 Formule :

```
Energie (Wh) = Puissance (W) × Durée (h)
```

---

### 🕒 2. Tranches horaires

| Tranche        | Heure     | Source principale |
| -------------- | --------- | ----------------- |
| Matin          | 06h → 17h | Panneau solaire   |
| Fin de journée | 17h → 19h | Panneau (50%)     |
| Nuit           | 19h → 06h | Batterie          |

---

### ☀️ 3. Production des panneaux solaires

* Seulement **40% de la puissance est réellement utilisable**

👉 Formule :

```
Puissance réelle = Puissance panneau × 0.4
```

* Entre **17h et 19h → 50% de production**

---

### 🔋 4. Batterie

* Capacité exprimée en **Wh ou kWh**
* Marge de sécurité : **+50%**

👉 Formule :

```
Capacité batterie réelle = besoin × 1.5
```

* Fonctionne uniquement **la nuit (19h → 06h)**

---

### 🔄 5. Recharge batterie

Pendant la journée :

* Le panneau :

  * alimente les appareils
  * recharge la batterie

👉 Règle importante :

> La batterie doit être **100% chargée à 17h**

---

### ⏱️ 6. Temps de charge batterie

👉 Formule :

```
Temps (h) = Capacité batterie (Wh) / Puissance disponible (W)
```

Exemples :

* 1000W → 1h pour 1000Wh
* 500W → 2h
* 100W → 10h

---

## 🧠 Logique globale du système

### Étape 1 : Séparer les consommations

* Appareils de **jour**
* Appareils de **nuit**

---

### Étape 2 : Calcul énergie totale

```
Energie totale jour = somme appareils (jour)
Energie totale nuit = somme appareils (nuit)
```

---

### Étape 3 : Calcul batterie

```
Batterie nécessaire = Energie nuit × 1.5
```

---

### Étape 4 : Calcul panneaux solaires

Le panneau doit couvrir :

* consommation jour
* recharge batterie

```
Besoin total jour = Energie jour + Energie nuit
```

Puis appliquer rendement :

```
Puissance panneau = Besoin total / (heures ensoleillées × 0.4)
```

---

## 🧱 Architecture du projet

### 📦 Modules Python

---

### 1. `models/`

#### `Appareil`

```python
- id
- nom
- puissance_w
- duree_h
- tranche (matin / soir / nuit)
```

---

### 2. `database/`

* Connexion SQL Server
* CRUD appareils

Tables :

```
Appareils
Consommations
Resultats
```

---

### 3. `services/`

#### `consommation_service.py`

* calcul énergie appareil
* calcul total jour / nuit

---

#### `batterie_service.py`

* calcul capacité batterie
* appliquer marge 50%

---

#### `panneau_service.py`

* calcul puissance panneau
* appliquer rendement 40%

---

#### `simulation_service.py`

* simuler une journée complète
* vérifier :

  * batterie chargée à 17h
  * autonomie nuit OK

---

### 4. `utils/`

* conversions (W ↔ kW, Wh ↔ kWh)
* gestion du temps

---

## 🗄️ Base de données (SQL Server)

### Table : `appareils`

```sql
id INT PRIMARY KEY IDENTITY
nom VARCHAR(100)
puissance_w FLOAT
duree_h FLOAT
tranche VARCHAR(20)
```

---

### Table : `resultats`

```sql
id INT PRIMARY KEY IDENTITY
energie_jour FLOAT
energie_nuit FLOAT
batterie_wh FLOAT
panneau_w FLOAT
date_calcul DATETIME
```

---

## ✅ TODO (à implémenter)

### 🔹 Phase 1 — Base

* [ ] Créer la base SQL Server
* [ ] Créer les tables
* [ ] Connexion Python → SQL Server

---

### 🔹 Phase 2 — Logique métier

* [ ] Implémenter calcul énergie appareil
* [ ] Implémenter séparation jour / nuit
* [ ] Implémenter calcul batterie
* [ ] Implémenter calcul panneau

---

### 🔹 Phase 3 — Simulation

* [ ] Simuler une journée complète
* [ ] Vérifier recharge batterie
* [ ] Gérer cas insuffisance énergie

---

### 🔹 Phase 4 — Interface

* [ ] CLI (terminal) ou GUI (Tkinter / Web)
* [ ] Ajouter appareils
* [ ] Afficher résultats

---

### 🔹 Phase 5 — Améliorations

* [ ] Ajouter météo (optionnel)
* [ ] Ajouter rendement variable
* [ ] Historique des calculs
* [ ] Export (PDF / Excel)

---

## 🚀 Résultat attendu

Le système doit fournir :

* 🔋 Capacité batterie recommandée
* ☀️ Puissance panneau recommandée
* 📊 Détail consommation (jour / nuit)

---
