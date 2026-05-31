# -*- coding: utf-8 -*-
"""
Configuration centralisée de l'application de recherche immobilière
Région de Dinan (Côtes-d'Armor, 22)
"""

# ---------------------------------------------------------------------------
# Communes cibles avec niveau de priorité pour le scoring
# Niveau 3 = priorité maximale, niveau 2 = priorité intermédiaire
# ---------------------------------------------------------------------------
COMMUNES_PRIORITAIRES = {
    "dinan": 3,
    "taden": 3,
    "léhon": 3,
    "lehon": 3,
    "saint-samson-sur-rance": 2,
    "saint samson sur rance": 2,
    "quevert": 2,
    "lancieux": 2,
    "saint-carné": 2,
    "saint carné": 2,
    "saint carne": 2,
}

# Communes dans un rayon ~10 km autour de Dinan (acceptées, priorité faible)
COMMUNES_RAYON = [
    "plancoët", "pleslin-trigavou", "corseul", "évran", "plorec-sur-arguenon",
    "saint-hélen", "saint helen", "calorguen", "la vicomté-sur-rance",
    "la vicomte-sur-rance", "saint-juvat", "ploubalay", "créhen", "crehen",
    "saint-cast-le-guildo", "pleudihen-sur-rance", "saint-solen", "la landec",
    "tressaint", "vildé-guingalan", "vilde-guingalan", "aucaleuc",
    "saint-andré-des-eaux", "saint andre des eaux", "pluduno",
]

# Toutes les communes connues (pour filtrage)
def toutes_communes() -> list:
    """Retourne la liste complète de toutes les communes connues."""
    communes = list(COMMUNES_PRIORITAIRES.keys()) + COMMUNES_RAYON
    # Déduplique en gardant les noms uniques
    vus = set()
    resultat = []
    for c in communes:
        c_norm = c.lower()
        if c_norm not in vus:
            vus.add(c_norm)
            resultat.append(c)
    return resultat


# ---------------------------------------------------------------------------
# Critères de filtrage (modifiables depuis la sidebar Streamlit)
# ---------------------------------------------------------------------------
CRITERES = {
    "loyer_max": 1000,              # €/mois, charges comprises
    "chambres_min": 3,              # Nombre minimum de chambres
    "inclure_appartements": False,  # Désactivé par défaut
}


# ---------------------------------------------------------------------------
# Paramètres du comportement du scraper
# ---------------------------------------------------------------------------
SCRAPER_SETTINGS = {
    "delay_min": 2,     # Secondes entre deux requêtes (min)
    "delay_max": 5,     # Secondes entre deux requêtes (max)
    "timeout": 30,      # Timeout HTTP en secondes
    "max_pages": 10,    # Nombre max de pages à scraper par site
    "user_agents": [
        # User-agents courants de navigateurs réels
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    ],
}


# ---------------------------------------------------------------------------
# Configuration PAP.fr (particuliers à particuliers)
# URL : location maison+appartement dans les Côtes-d'Armor, ≥4 pièces, ≤1000€
# Note : "4 pièces" = 3 chambres + séjour → correspond à "3 chambres min"
# ---------------------------------------------------------------------------
PAP_CONFIG = {
    "nom": "PAP.fr",
    "actif": True,
    "base_url": "https://www.pap.fr",
    "search_url": (
        "https://www.pap.fr/annonce/location-maison-appartement"
        "-22-cotes-d-armor-g3228"
        "?nb-pieces-min=4&loyer-max=1000&tri=ajout-desc"
    ),
    # Sélecteurs CSS — à mettre à jour si PAP.fr change son HTML
    "selectors": {
        "liste_annonces": "article.search-list-item, div.search-list-item, li.result",
        "titre": "h2.search-list-item-title, .item-title, h2.title",
        "prix": "span.price, .loyer, strong.price, [class*='price']",
        "localisation": ".search-list-item-description strong, .location, .ville",
        "description": ".search-list-item-description, .description, .details",
        "lien": "a.search-list-item-link, a[href*='/annonce/'], a[href*='/location/']",
        "pagination_suivante": (
            "a.pagination-next, a[aria-label='Page suivante'], "
            "a[rel='next'], li.next a, .pager-next a"
        ),
    },
}


# ---------------------------------------------------------------------------
# Configuration Ouest-France Immo
# ---------------------------------------------------------------------------
OUEST_FRANCE_CONFIG = {
    "nom": "Ouest-France Immo",
    "actif": True,
    "base_url": "https://immobilier.ouest-france.fr",
    "search_url": (
        "https://immobilier.ouest-france.fr/immobilier/location/maison/"
        "?localisation=Dinan%2C+Taden%2C+L%C3%A9hon%2C+Quevert%2C+Lancieux"
        "&prix-max=1000&nb-pieces-min=4"
    ),
    "selectors": {
        "liste_annonces": (
            "article.offer, div.offer-card, li[class*='offer'], "
            ".annonce, article[class*='card']"
        ),
        "titre": "h2, h3, .offer-title, .card-title, [class*='title']",
        "prix": ".price, .offer-price, [class*='prix'], [class*='price']",
        "localisation": ".location, .localisation, .ville, [class*='location']",
        "description": ".description, .offer-desc, .card-description",
        "lien": "a[href*='/immobilier/'], a[href*='/annonce/'], a.card-link",
        "pagination_suivante": (
            "a.pagination-next, a[aria-label='Suivant'], "
            "a[rel='next'], .pagination a:last-child"
        ),
    },
}

# ---------------------------------------------------------------------------
# Registre de toutes les configurations de scrapers disponibles
# Commentez une entrée pour désactiver un scraper
# ---------------------------------------------------------------------------
SCRAPERS_CONFIG = [
    PAP_CONFIG,
    OUEST_FRANCE_CONFIG,
]


# ---------------------------------------------------------------------------
# Fichier de sortie Excel
# ---------------------------------------------------------------------------
EXCEL_PATH = "data/annonces_dinan.xlsx"

# Colonnes du tableau Excel (dans l'ordre d'affichage)
COLONNES_EXCEL = [
    "Commune",
    "Type",
    "Loyer (€)",
    "Charges",       # "CC" = charges comprises, "HC" = hors charges
    "Chambres",
    "Surface (m²)",
    "DPE",
    "Lien",
    "Date repérée",
    "Source",
    "Nouveau",       # "Oui" si annonce absente lors du dernier passage
    "Score",         # 0-100 selon critères de priorité
]
