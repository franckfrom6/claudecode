# -*- coding: utf-8 -*-
"""
Scraper pour PAP.fr (Particuliers à Particuliers).
Site HTML statique — requests + BeautifulSoup suffisent.

URL de recherche configurée dans config.PAP_CONFIG["search_url"].
Sélecteurs CSS dans config.PAP_CONFIG["selectors"].
"""

import re
import logging
from typing import Optional
from urllib.parse import urljoin

from scrapers.base import BaseScraper
from config import PAP_CONFIG, SCRAPER_SETTINGS, COMMUNES_PRIORITAIRES, COMMUNES_RAYON

logger = logging.getLogger(__name__)

# Mots-clés pour détecter le type de bien dans le texte
_MOTS_MAISON = ["maison", "villa", "pavillon", "fermette", "longère", "longere", "chalet", "corps de ferme"]
_MOTS_APPART = ["appartement", "appart", "studio", "duplex", "triplex", "loft"]


class PAPScraper(BaseScraper):
    """Scraper PAP.fr — particuliers à particuliers, HTML accessible."""

    def __init__(self):
        super().__init__(PAP_CONFIG)
        self.search_url = PAP_CONFIG["search_url"]

    # ------------------------------------------------------------------
    # Point d'entrée principal
    # ------------------------------------------------------------------

    def scrape(self, callback_progression=None) -> list:
        """Scrape toutes les pages de résultats et retourne les annonces trouvées."""
        annonces = []
        url_courante = self.search_url
        page_num = 0

        logger.info(f"[{self.nom}] Démarrage → {self.search_url}")

        while url_courante and page_num < SCRAPER_SETTINGS["max_pages"]:
            page_num += 1
            logger.info(f"[{self.nom}] Page {page_num} : {url_courante}")

            if callback_progression:
                callback_progression(f"PAP.fr — scraping page {page_num}…")

            # Vérification robots.txt uniquement à la première page
            if page_num == 1 and not self.verifier_robots(url_courante):
                logger.warning(f"[{self.nom}] Arrêt — robots.txt interdit l'accès")
                break

            soup = self.get_page(url_courante, attendre=(page_num > 1))
            if soup is None:
                logger.error(f"[{self.nom}] Page {page_num} inaccessible — arrêt")
                break

            nouvelles = self._extraire_annonces(soup)

            if not nouvelles:
                logger.info(f"[{self.nom}] Aucune annonce page {page_num} — fin de pagination")
                break

            annonces.extend(nouvelles)
            logger.info(
                f"[{self.nom}] {len(nouvelles)} annonces page {page_num} "
                f"(total : {len(annonces)})"
            )

            url_courante = self._page_suivante(soup, url_courante)

        logger.info(f"[{self.nom}] Terminé — {len(annonces)} annonces brutes")
        return annonces

    # ------------------------------------------------------------------
    # Extraction d'une page complète
    # ------------------------------------------------------------------

    def _extraire_annonces(self, soup) -> list:
        """Extrait toutes les annonces d'une page de résultats PAP.fr."""

        # Sélecteur principal puis fallbacks si le HTML a changé
        items = soup.select(self.selectors["liste_annonces"])

        if not items:
            # Fallbacks progressifs — à mettre à jour si le site change de structure
            for sel_fallback in [
                "article[class*='search']",
                "div[class*='result']",
                "li[class*='annonce']",
                "div[class*='annonce']",
                "article",
            ]:
                items = soup.select(sel_fallback)
                if items:
                    logger.warning(
                        f"[{self.nom}] Sélecteur principal absent — fallback '{sel_fallback}' "
                        f"({len(items)} items)"
                    )
                    break

        if not items:
            logger.warning(f"[{self.nom}] Aucun item trouvé — vérifiez les sélecteurs CSS")
            # Log les 500 premiers chars pour faciliter le débogage
            logger.debug(f"[{self.nom}] HTML reçu (500c) : {str(soup)[:500]}")
            return []

        annonces = []
        for item in items:
            try:
                ann = self._extraire_annonce(item)
                if ann:
                    annonces.append(ann)
            except Exception as e:
                logger.warning(f"[{self.nom}] Erreur parsing item : {e}")

        return annonces

    # ------------------------------------------------------------------
    # Extraction d'une annonce individuelle
    # ------------------------------------------------------------------

    def _extraire_annonce(self, item) -> Optional[dict]:
        """Parse un bloc HTML d'annonce et retourne un dict normalisé."""
        ann = self.annonce_vide()
        ann["source"] = self.nom

        # -- Lien --
        lien_tag = item.select_one(self.selectors["lien"]) or item.select_one("a[href]")
        if lien_tag:
            href = lien_tag.get("href", "")
            ann["lien"] = urljoin(self.base_url, href) if href else None

        # -- Texte complet de l'item (pour extraction regex) --
        texte = item.get_text(separator=" ", strip=True).lower()

        # -- Titre --
        titre_tag = item.select_one(self.selectors["titre"])
        titre = titre_tag.get_text(strip=True) if titre_tag else texte[:80]

        # -- Type de bien --
        ann["type"] = self._detecter_type(texte)

        # -- Prix et charges --
        prix_tag = item.select_one(self.selectors["prix"])
        texte_prix = prix_tag.get_text(strip=True) if prix_tag else texte
        ann["loyer"], ann["charges"] = self._extraire_prix(texte_prix)

        # Si non trouvé dans la balise prix dédiée, on cherche dans tout le texte
        if not ann["loyer"]:
            ann["loyer"], ann["charges"] = self._extraire_prix(texte)

        # -- Commune --
        ann["commune"] = self._extraire_commune(texte)

        # -- Chambres --
        ann["chambres"] = self._extraire_chambres(texte)

        # -- Surface --
        ann["surface"] = self._extraire_surface(texte)

        # -- DPE --
        ann["dpe"] = self._extraire_dpe(texte)

        # -- Hash de déduplication --
        ann["hash"] = self.calculer_hash(
            ann.get("lien") or "",
            titre,
            str(ann.get("loyer") or ""),
        )

        # Rejette les items sans lien ET sans prix (probablement du bruit HTML)
        if not ann["lien"] and ann["loyer"] is None:
            return None

        return ann

    # ------------------------------------------------------------------
    # Parsers d'extraction (regex)
    # ------------------------------------------------------------------

    @staticmethod
    def _detecter_type(texte: str) -> str:
        """Détecte si l'annonce concerne une maison ou un appartement."""
        if any(m in texte for m in _MOTS_MAISON):
            return "Maison"
        if any(m in texte for m in _MOTS_APPART):
            return "Appartement"
        return "Inconnu"

    @staticmethod
    def _extraire_prix(texte: str) -> tuple:
        """
        Retourne (loyer_int, charges_str) depuis un texte de prix.
        charges_str vaut "CC" (charges comprises) ou "HC" (hors charges).
        Ex : "850 € CC/mois" → (850, "CC")
        """
        # Pattern : nombre optionnellement espacé suivi du symbole euro
        pattern = (
            r"(\d[\d\s ]*)"          # montant (ex : "1 050" ou "850")
            r"\s*[€£]"                    # symbole monétaire
            r"(?:\s*/\s*mois)?"           # "/mois" optionnel
            r"\s*"
            r"(CC|HC|ch(?:arges?)?\s*(?:comprises?|incluses?)|hors\s*charges?)?"
        )
        match = re.search(pattern, texte, re.IGNORECASE)
        if not match:
            return None, None

        try:
            # Supprime espaces insécables et espaces classiques dans le montant
            loyer = int(re.sub(r"[\s  ]", "", match.group(1)))
        except (ValueError, TypeError):
            return None, None

        # Interprétation des charges
        charges_raw = (match.group(2) or "").lower()
        if re.search(r"cc|comprises?|incluses?", charges_raw):
            charges = "CC"
        elif re.search(r"hc|hors", charges_raw):
            charges = "HC"
        else:
            charges = "HC"  # Hypothèse conservatrice par défaut

        return loyer, charges

    @staticmethod
    def _extraire_commune(texte: str) -> Optional[str]:
        """Détecte la commune à partir du texte d'une annonce."""
        texte_lower = texte.lower()

        # Communes prioritaires d'abord (liste config)
        for commune, _ in COMMUNES_PRIORITAIRES.items():
            if commune in texte_lower:
                return commune.title()

        # Communes du rayon 10 km
        for commune in COMMUNES_RAYON:
            if commune.lower() in texte_lower:
                return commune.title()

        # Fallback : code postal 22xxx
        match = re.search(r"\b(22\d{3})\b", texte)
        if match:
            return f"CP {match.group(1)}"

        return None

    @staticmethod
    def _extraire_chambres(texte: str) -> Optional[int]:
        """
        Extrait le nombre de chambres depuis le texte.
        Gère : "3 chambres", "T4", "F3", "4 pièces".
        """
        # Nombre de chambres explicite
        m = re.search(r"(\d+)\s*ch(?:ambre)?s?\b", texte, re.IGNORECASE)
        if m:
            return int(m.group(1))

        # Type T4 / F4 → chambres = pièces - 1 (on retire le séjour)
        m = re.search(r"\b[tf](\d+)\b", texte, re.IGNORECASE)
        if m:
            n = int(m.group(1))
            return max(n - 1, 1)

        # "4 pièces" → chambres = pièces - 1
        m = re.search(r"(\d+)\s*pi[èe]ces?\b", texte, re.IGNORECASE)
        if m:
            n = int(m.group(1))
            return max(n - 1, 1)

        return None

    @staticmethod
    def _extraire_surface(texte: str) -> Optional[int]:
        """Extrait la surface en m² depuis le texte."""
        m = re.search(r"(\d+)\s*m[²2²]", texte, re.IGNORECASE)
        if m:
            return int(m.group(1))
        return None

    @staticmethod
    def _extraire_dpe(texte: str) -> Optional[str]:
        """Extrait la lettre DPE (A-G) si mentionnée dans le texte."""
        patterns = [
            r"dpe\s*[:\-=]?\s*([a-g])\b",
            r"classe[s]?\s+[éeE]nerg[ée]tique[s]?\s*[:\-=]?\s*([a-g])\b",
            r"[éeE]tiquette\s+[éeE]nerg[ée]tique\s*[:\-=]?\s*([a-g])\b",
            r"\bénergie\s*[:\-=]?\s*([a-g])\b",
        ]
        for pattern in patterns:
            m = re.search(pattern, texte, re.IGNORECASE)
            if m:
                return m.group(1).upper()
        return None

    # ------------------------------------------------------------------
    # Pagination
    # ------------------------------------------------------------------

    def _page_suivante(self, soup, url_courante: str) -> Optional[str]:
        """Retourne l'URL de la page suivante, ou None si dernière page."""
        sel = self.selectors["pagination_suivante"]
        lien = soup.select_one(sel)

        if not lien:
            # Fallbacks supplémentaires
            for sel_fb in [
                "a[title*='uivant']", "a[class*='next']",
                "a[aria-label*='uivant']",
            ]:
                lien = soup.select_one(sel_fb)
                if lien:
                    break

        if not lien:
            return None

        href = lien.get("href", "")
        if not href or href in ("#", "javascript:void(0)"):
            return None

        url = urljoin(url_courante, href)
        # Évite les boucles infinies
        return url if url != url_courante else None
