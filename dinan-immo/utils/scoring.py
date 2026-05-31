# -*- coding: utf-8 -*-
"""
Calcul du score 0-100 pour chaque annonce.

Critères et pondérations :
- Commune prioritaire  : 0-30 pts
- Loyer bas            : 0-30 pts
- DPE bon (A-D)        : 0-20 pts
- Nombre de chambres   : 0-20 pts
"""

from config import COMMUNES_PRIORITAIRES, COMMUNES_RAYON


def calculer_score(annonce: dict) -> int:
    """Retourne un entier entre 0 et 100 reflétant l'intérêt de l'annonce."""
    score = 0

    # ------------------------------------------------------------------
    # Commune (30 pts max)
    # Niveau 3 = communes de premier choix (Dinan, Taden, Léhon)
    # Niveau 2 = communes de second choix (Quevert, Lancieux, …)
    # Rayon 10 km = 10 pts
    # ------------------------------------------------------------------
    commune = (annonce.get("commune") or "").lower().strip()
    if commune:
        niveau = COMMUNES_PRIORITAIRES.get(commune)
        if niveau == 3:
            score += 30
        elif niveau == 2:
            score += 20
        elif any(c.lower() in commune for c in COMMUNES_RAYON):
            score += 10
        # Commune dans le code postal 22xxx mais non reconnue → 5 pts
        elif commune.startswith("cp 22"):
            score += 5

    # ------------------------------------------------------------------
    # Loyer (30 pts max)
    # Moins c'est cher, plus le score est élevé
    # ------------------------------------------------------------------
    loyer = annonce.get("loyer")
    if loyer is not None:
        try:
            loyer = int(loyer)
            if loyer <= 600:
                score += 30
            elif loyer <= 700:
                score += 25
            elif loyer <= 800:
                score += 18
            elif loyer <= 900:
                score += 10
            elif loyer <= 1000:
                score += 5
        except (ValueError, TypeError):
            pass

    # ------------------------------------------------------------------
    # DPE (20 pts max)
    # ------------------------------------------------------------------
    dpe = (annonce.get("dpe") or "").upper().strip()
    dpe_pts = {"A": 20, "B": 16, "C": 12, "D": 7, "E": 2, "F": 0, "G": 0}
    score += dpe_pts.get(dpe, 0)

    # ------------------------------------------------------------------
    # Chambres (20 pts max)
    # ------------------------------------------------------------------
    chambres = annonce.get("chambres")
    if chambres is not None:
        try:
            n = int(chambres)
            if n >= 5:
                score += 20
            elif n == 4:
                score += 15
            elif n == 3:
                score += 10
        except (ValueError, TypeError):
            pass

    return min(score, 100)
