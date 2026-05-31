# -*- coding: utf-8 -*-
"""
Registre des scrapers immobiliers.

Pour ajouter un nouveau scraper :
1. Créer scraper/mon_agence.py avec une classe héritant de BaseScraper
2. Importer la classe ci-dessous
3. L'ajouter dans SCRAPERS_CLASSES
"""

import logging
from config import SCRAPERS_CONFIG

logger = logging.getLogger(__name__)


def obtenir_scrapers() -> list:
    """
    Instancie et retourne tous les scrapers marqués actif=True dans la config.
    Chaque import est fait à la demande pour isoler les erreurs d'import.
    """
    from scrapers.pap import PAPScraper
    from scrapers.ouest_france import OuestFranceScraper

    # Correspondance nom_config → classe scraper
    CLASSES = {
        "PAP.fr": PAPScraper,
        "Ouest-France Immo": OuestFranceScraper,
    }

    scrapers = []
    for cfg in SCRAPERS_CONFIG:
        if not cfg.get("actif", True):
            continue
        nom = cfg.get("nom", "")
        cls = CLASSES.get(nom)
        if cls is None:
            logger.warning(f"Aucune classe trouvée pour le scraper '{nom}'")
            continue
        try:
            scrapers.append(cls())
        except Exception as e:
            logger.error(f"Impossible d'initialiser {nom} : {e}")

    return scrapers
