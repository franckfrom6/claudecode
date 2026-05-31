# -*- coding: utf-8 -*-
"""
Classe de base pour tous les scrapers immobiliers.
Fournit : session HTTP, vérification robots.txt, throttling, parsing HTML.
"""

import time
import random
import logging
import hashlib
from abc import ABC, abstractmethod
from typing import Optional
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

import requests
from bs4 import BeautifulSoup

from config import SCRAPER_SETTINGS

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Classe de base — chaque scraper hérite de cette classe."""

    def __init__(self, config: dict):
        self.config = config
        self.nom = config.get("nom", "Inconnu")
        self.base_url = config.get("base_url", "")
        self.selectors = config.get("selectors", {})
        self.session = self._creer_session()
        self._robots: Optional[RobotFileParser] = None

    # ------------------------------------------------------------------
    # Session HTTP
    # ------------------------------------------------------------------

    def _creer_session(self) -> requests.Session:
        """Crée une session HTTP avec un User-Agent aléatoire parmi ceux définis."""
        session = requests.Session()
        ua = random.choice(SCRAPER_SETTINGS["user_agents"])
        session.headers.update({
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
        })
        return session

    # ------------------------------------------------------------------
    # robots.txt
    # ------------------------------------------------------------------

    def verifier_robots(self, url: str) -> bool:
        """
        Vérifie si l'URL est autorisée par le robots.txt du domaine.
        En cas d'erreur de lecture, retourne True (on scrape prudemment).
        """
        try:
            if self._robots is None:
                parsed = urlparse(url)
                robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
                self._robots = RobotFileParser()
                self._robots.set_url(robots_url)
                self._robots.read()

            ua = self.session.headers.get("User-Agent", "*")
            autorise = self._robots.can_fetch(ua, url)

            if not autorise:
                logger.warning(f"[{self.nom}] robots.txt interdit : {url}")

            return autorise

        except Exception as e:
            logger.warning(f"[{self.nom}] Lecture robots.txt impossible ({e}) — on continue")
            return True

    # ------------------------------------------------------------------
    # Récupération de page
    # ------------------------------------------------------------------

    def get_page(self, url: str, attendre: bool = True) -> Optional[BeautifulSoup]:
        """
        Télécharge une page HTML avec délai anti-bot et gestion robuste des erreurs.
        Retourne None si la page est inaccessible (pas d'exception propagée).
        """
        if attendre:
            delai = random.uniform(SCRAPER_SETTINGS["delay_min"], SCRAPER_SETTINGS["delay_max"])
            logger.debug(f"[{self.nom}] Pause {delai:.1f}s…")
            time.sleep(delai)

        try:
            resp = self.session.get(
                url,
                timeout=SCRAPER_SETTINGS["timeout"],
                allow_redirects=True,
            )
            resp.raise_for_status()
            resp.encoding = resp.apparent_encoding  # évite les problèmes d'accents
            return BeautifulSoup(resp.text, "lxml")

        except requests.HTTPError as e:
            code = e.response.status_code if e.response else "?"
            logger.error(f"[{self.nom}] HTTP {code} — {url}")
        except requests.ConnectionError:
            logger.error(f"[{self.nom}] Connexion impossible — {url}")
        except requests.Timeout:
            logger.error(f"[{self.nom}] Délai dépassé — {url}")
        except Exception as e:
            logger.error(f"[{self.nom}] Erreur inattendue sur {url} : {e}")

        return None

    # ------------------------------------------------------------------
    # Utilitaires
    # ------------------------------------------------------------------

    @staticmethod
    def calculer_hash(url: str, titre: str, prix: str) -> str:
        """Hash MD5 utilisé pour la déduplication (URL + titre + prix)."""
        contenu = f"{url}|{titre}|{prix}".lower().strip()
        return hashlib.md5(contenu.encode("utf-8")).hexdigest()

    @staticmethod
    def annonce_vide() -> dict:
        """Retourne un dictionnaire d'annonce avec tous les champs à None."""
        return {
            "commune": None,
            "type": None,
            "loyer": None,
            "charges": None,
            "chambres": None,
            "surface": None,
            "dpe": None,
            "lien": None,
            "source": None,
            "hash": None,
        }

    # ------------------------------------------------------------------
    # Méthode abstraite — à implémenter dans chaque scraper
    # ------------------------------------------------------------------

    @abstractmethod
    def scrape(self, callback_progression=None) -> list:
        """
        Lance le scraping et retourne une liste de dicts (un par annonce).
        callback_progression(message: str) est appelé à chaque avancement.
        """
