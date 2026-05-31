# -*- coding: utf-8 -*-
"""
Déduplication des annonces et enrichissement avant sauvegarde.

Pipeline :
1. Supprime les doublons inter-scrapers (même session)
2. Marque les annonces absentes du fichier Excel comme "Nouveau"
3. Filtre selon les critères (loyer, chambres, type, commune)
4. Calcule le score de chaque annonce retenue
5. Trie par score décroissant
"""

import logging
from datetime import datetime

from utils.excel_writer import charger_hashs_existants
from utils.scoring import calculer_score
from config import CRITERES, COMMUNES_PRIORITAIRES, COMMUNES_RAYON

logger = logging.getLogger(__name__)


def dedupliquer_et_enrichir(annonces: list, criteres: dict = None) -> list:
    """
    Déduplique, filtre et enrichit la liste d'annonces brutes.
    criteres : dict optionnel pour surcharger les critères de config.py.
    """
    crit = {**CRITERES, **(criteres or {})}

    # Hashs des annonces déjà présentes dans le fichier Excel
    hashs_connus = charger_hashs_existants()

    vus = set()        # Déduplication intra-session (plusieurs scrapers)
    retenues = []
    nb_doublons = 0
    nb_filtrees = 0

    for ann in annonces:
        h = ann.get("hash")

        # -- Déduplication --
        if not h or h in vus:
            nb_doublons += 1
            continue
        vus.add(h)

        # -- Filtrage critères --
        if not _respecte_criteres(ann, crit):
            nb_filtrees += 1
            continue

        # -- Marquage nouveau --
        ann["nouveau"] = (h not in hashs_connus)

        # -- Date de repérage --
        ann["date_reperee"] = datetime.now().strftime("%Y-%m-%d")

        # -- Score --
        ann["score"] = calculer_score(ann)

        retenues.append(ann)

    nb_nouvelles = sum(1 for a in retenues if a.get("nouveau"))
    logger.info(
        f"Déduplication : {len(retenues)} retenues, "
        f"{nb_doublons} doublons, "
        f"{nb_filtrees} filtrées par critères, "
        f"{nb_nouvelles} nouvelles"
    )

    # Tri par score décroissant
    retenues.sort(key=lambda a: a.get("score", 0), reverse=True)
    return retenues


def _respecte_criteres(ann: dict, crit: dict) -> bool:
    """Retourne True si l'annonce passe tous les filtres."""

    # Loyer maximum
    loyer = ann.get("loyer")
    if loyer is not None:
        try:
            if int(loyer) > int(crit["loyer_max"]):
                return False
        except (ValueError, TypeError):
            pass  # Loyer non parsé — on laisse passer pour inspection manuelle

    # Chambres minimum
    chambres = ann.get("chambres")
    if chambres is not None:
        try:
            if int(chambres) < int(crit["chambres_min"]):
                return False
        except (ValueError, TypeError):
            pass

    # Type de bien
    if not crit.get("inclure_appartements", False):
        type_bien = (ann.get("type") or "").lower()
        if type_bien == "appartement":
            return False

    # Commune dans la zone cible
    commune = (ann.get("commune") or "").lower().strip()
    if commune and not commune.startswith("cp 22"):
        dans_zone = (
            commune in COMMUNES_PRIORITAIRES
            or any(c.lower() in commune for c in COMMUNES_RAYON)
        )
        if not dans_zone:
            return False

    return True
