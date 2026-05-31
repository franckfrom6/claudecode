# -*- coding: utf-8 -*-
"""
Scraper pour Ouest-France Immo (immobilier.ouest-france.fr).
Site avec ancrage Bretagne, HTML globalement statique.

Structure similaire à pap.py — hérite des méthodes d'extraction de BaseScraper
et redéfinit uniquement ce qui est spécifique au site.
"""

import re
import logging
from typing import Optional
from urllib.parse import urljoin

from scrapers.base import BaseScraper
from scrapers.pap import PAPScraper  # Réutilise les méthodes d'extraction regex
from config import OUEST_FRANCE_CONFIG, SCRAPER_SETTINGS

logger = logging.getLogger(__name__)


class OuestFranceScraper(PAPScraper):
    """
    Scraper Ouest-France Immo.
    Hérite de PAPScraper pour réutiliser les méthodes d'extraction regex
    (prix, commune, chambres, surface, DPE) — seuls les sélecteurs CSS diffèrent.
    """

    def __init__(self):
        # On appelle BaseScraper directement (pas PAPScraper.__init__)
        BaseScraper.__init__(self, OUEST_FRANCE_CONFIG)
        self.search_url = OUEST_FRANCE_CONFIG["search_url"]

    # ------------------------------------------------------------------
    # Point d'entrée principal (identique à PAPScraper)
    # ------------------------------------------------------------------

    def scrape(self, callback_progression=None) -> list:
        """Scrape toutes les pages Ouest-France Immo et retourne les annonces."""
        annonces = []
        url_courante = self.search_url
        page_num = 0

        logger.info(f"[{self.nom}] Démarrage → {self.search_url}")

        while url_courante and page_num < SCRAPER_SETTINGS["max_pages"]:
            page_num += 1
            logger.info(f"[{self.nom}] Page {page_num} : {url_courante}")

            if callback_progression:
                callback_progression(f"Ouest-France Immo — scraping page {page_num}…")

            if page_num == 1 and not self.verifier_robots(url_courante):
                logger.warning(f"[{self.nom}] Arrêt — robots.txt interdit l'accès")
                break

            soup = self.get_page(url_courante, attendre=(page_num > 1))
            if soup is None:
                logger.error(f"[{self.nom}] Page {page_num} inaccessible — arrêt")
                break

            nouvelles = self._extraire_annonces(soup)

            if not nouvelles:
                logger.info(f"[{self.nom}] Aucune annonce page {page_num} — fin")
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
    # Extraction (légère surcharge pour les fallbacks spécifiques à OF)
    # ------------------------------------------------------------------

    def _extraire_annonces(self, soup) -> list:
        """Extrait les annonces d'une page Ouest-France Immo."""
        items = soup.select(self.selectors["liste_annonces"])

        if not items:
            # Fallbacks pour le CMS Ouest-France
            for sel_fb in [
                "article[class*='card']",
                "div[class*='offer']",
                "div[class*='annonce']",
                "li[class*='result']",
            ]:
                items = soup.select(sel_fb)
                if items:
                    logger.warning(
                        f"[{self.nom}] Sélecteur de secours utilisé : '{sel_fb}' "
                        f"({len(items)} items)"
                    )
                    break

        if not items:
            logger.warning(f"[{self.nom}] Aucun item — vérifiez les sélecteurs CSS")
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

    def _extraire_annonce(self, item) -> Optional[dict]:
        """Parse un bloc HTML Ouest-France Immo."""
        ann = self.annonce_vide()
        ann["source"] = self.nom

        # -- Lien --
        lien_tag = item.select_one(self.selectors["lien"]) or item.select_one("a[href]")
        if lien_tag:
            href = lien_tag.get("href", "")
            # Certains liens OF sont relatifs, d'autres absolus
            if href and not href.startswith("http"):
                href = urljoin(self.base_url, href)
            ann["lien"] = href or None

        # -- Texte complet --
        texte = item.get_text(separator=" ", strip=True).lower()

        # -- Titre --
        titre_tag = item.select_one(self.selectors["titre"])
        titre = titre_tag.get_text(strip=True) if titre_tag else texte[:80]

        # -- Type de bien --
        ann["type"] = self._detecter_type(texte)

        # -- Prix --
        prix_tag = item.select_one(self.selectors["prix"])
        texte_prix = prix_tag.get_text(strip=True) if prix_tag else texte
        ann["loyer"], ann["charges"] = self._extraire_prix(texte_prix)
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

        # -- Hash --
        ann["hash"] = self.calculer_hash(
            ann.get("lien") or "",
            titre,
            str(ann.get("loyer") or ""),
        )

        if not ann["lien"] and ann["loyer"] is None:
            return None

        return ann
