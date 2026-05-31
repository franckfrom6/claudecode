# Locations Dinan — Scraper immobilier

Application de recherche de logements à louer dans la région de Dinan (Côtes-d'Armor, 22).  
Interface web locale en français, accessible depuis n'importe quel navigateur.

---

## Prérequis

- **Python 3.10 ou plus récent** ([télécharger](https://www.python.org/downloads/))
- Connexion Internet active lors du scraping

---

## Installation et lancement

### Windows

1. Télécharger ou cloner ce dossier sur votre ordinateur
2. **Double-cliquer sur `launch.bat`**  
   → installe automatiquement les dépendances, ouvre le navigateur sur `http://localhost:8501`

### macOS / Linux

```bash
chmod +x launch.sh
./launch.sh
```

→ Ouvre automatiquement `http://localhost:8501`

### Lancement manuel (toutes plateformes)

```bash
cd dinan-immo
python -m venv .venv
# Windows : .venv\Scripts\activate
# Mac/Linux : source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

---

## Utilisation

1. Ajustez les **critères** dans la barre latérale (loyer max, chambres, type de bien)
2. Cliquez sur le grand bouton **Lancer la recherche**
3. Attendez la fin du scraping (1 à 3 minutes selon les sites)
4. Consultez le tableau, filtrez par commune ou source
5. Téléchargez le résultat avec **Télécharger le tableau en Excel**

Le fichier `data/annonces_dinan.xlsx` est mis à jour automatiquement à chaque recherche.  
Les nouvelles annonces sont surlignées en **jaune** et marquées **🆕 Oui**.

---

## Structure du projet

```
dinan-immo/
├── app.py                    # Interface Streamlit
├── config.py                 # Configuration centrale (URLs, communes, critères)
├── requirements.txt
├── launch.sh                 # Démarrage Linux/macOS
├── launch.bat                # Démarrage Windows
├── data/
│   └── annonces_dinan.xlsx   # Base d'annonces (créée au 1er lancement)
├── scrapers/
│   ├── __init__.py           # Registre des scrapers
│   ├── base.py               # Classe abstraite commune
│   ├── pap.py                # Scraper PAP.fr
│   └── ouest_france.py       # Scraper Ouest-France Immo
└── utils/
    ├── deduplication.py      # Filtrage et déduplication
    ├── scoring.py            # Calcul du score 0-100
    └── excel_writer.py       # Lecture/écriture du fichier Excel
```

---

## Ajouter un scraper pour une agence locale

1. Créer `scrapers/mon_agence.py` :

```python
from scrapers.pap import PAPScraper
from config import MON_AGENCE_CONFIG  # à ajouter dans config.py

class MonAgenceScraper(PAPScraper):
    def __init__(self):
        BaseScraper.__init__(self, MON_AGENCE_CONFIG)
        self.search_url = MON_AGENCE_CONFIG["search_url"]
```

2. Dans `config.py`, ajouter la configuration :

```python
MON_AGENCE_CONFIG = {
    "nom": "Agence XYZ",
    "actif": True,
    "base_url": "https://www.agence-xyz.fr",
    "search_url": "https://www.agence-xyz.fr/location/?type=maison",
    "selectors": {
        "liste_annonces": "article.annonce",
        "titre": "h2.titre",
        "prix": ".prix",
        ...
    },
}
```

3. L'ajouter dans `scrapers/__init__.py` :

```python
from scrapers.mon_agence import MonAgenceScraper
CLASSES = {
    ...
    "Agence XYZ": MonAgenceScraper,
}
```

4. L'activer dans `SCRAPERS_CONFIG` de `config.py`.

---

## Lancement automatique quotidien

### Linux/macOS — cron

```bash
crontab -e
# Ajouter la ligne suivante (recherche chaque jour à 8h00) :
0 8 * * * /chemin/vers/dinan-immo/launch.sh >> /tmp/dinan-immo.log 2>&1
```

### Windows — Planificateur de tâches

1. Ouvrir le **Planificateur de tâches** (chercher dans le menu démarrer)
2. Créer une tâche de base → Déclencher : tous les jours à 8h00
3. Action : démarrer un programme → `C:\...\dinan-immo\launch.bat`

---

## Scoring des annonces (0–100)

| Critère             | Points max |
|---------------------|-----------|
| Commune prioritaire (Dinan/Taden/Léhon) | 30 |
| Loyer bas (≤ 600 €) | 30 |
| DPE bon (classe A)  | 20 |
| 5 chambres ou plus  | 20 |

---

## Sources scrapées

| Site | Type | Sélection |
|------|------|-----------|
| PAP.fr | Particuliers | ✅ Activé |
| Ouest-France Immo | Agences + particuliers | ✅ Activé |
| Agences locales Dinan | À configurer | ➕ Ajout facile |

**Sites délibérément exclus** : Leboncoin, SeLoger, Bien'ici, Logic-immo  
(protégés par DataDome/captchas — génèrent des erreurs systématiques)
