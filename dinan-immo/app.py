# -*- coding: utf-8 -*-
"""
Application Streamlit — Recherche de locations dans la région de Dinan.
Lancement : streamlit run app.py
"""

import os
import logging
from datetime import datetime
from io import BytesIO

import pandas as pd
import streamlit as st

from scrapers import obtenir_scrapers
from utils.deduplication import dedupliquer_et_enrichir
from utils.excel_writer import sauvegarder_annonces
from config import CRITERES, COLONNES_EXCEL, EXCEL_PATH, COMMUNES_PRIORITAIRES, COMMUNES_RAYON

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s : %(message)s",
    datefmt="%H:%M:%S",
)

# ---------------------------------------------------------------------------
# Configuration Streamlit
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Locations Dinan",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Bouton principal proéminent */
    div[data-testid="stButton"] > button[kind="primary"] {
        background-color: #1F6AA5;
        color: white;
        font-size: 1.15rem;
        font-weight: 700;
        padding: 0.8rem 1.5rem;
        border-radius: 8px;
        border: none;
        width: 100%;
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        background-color: #155a8a;
        border: none;
    }
    /* Badges */
    .badge-nouveau {
        background:#ffd700; color:#333; padding:2px 7px;
        border-radius:4px; font-size:0.8rem; font-weight:700;
    }
    /* Largeur du tableau */
    .stDataFrame { width: 100% !important; }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "annonces" not in st.session_state:
    st.session_state.annonces = []
if "logs" not in st.session_state:
    st.session_state.logs = []
if "derniere_recherche" not in st.session_state:
    st.session_state.derniere_recherche = None


# ---------------------------------------------------------------------------
# Fonctions utilitaires
# ---------------------------------------------------------------------------

def lancer_scraping(criteres_ui: dict, placeholder_log) -> list:
    """
    Instancie tous les scrapers actifs, les lance séquentiellement,
    puis déduplique et filtre les résultats.
    """
    scrapers = obtenir_scrapers()
    logs = []
    toutes_annonces = []

    def ajouter_log(msg: str):
        horodatage = datetime.now().strftime("%H:%M:%S")
        logs.append(f"[{horodatage}] {msg}")
        # Affiche les 20 dernières lignes dans le placeholder
        placeholder_log.code("\n".join(logs[-20:]), language=None)

    ajouter_log(f"Démarrage — {len(scrapers)} scraper(s) activé(s)")

    for scraper in scrapers:
        ajouter_log(f"⏳  {scraper.nom} — connexion…")
        try:
            annonces_site = scraper.scrape(
                callback_progression=lambda etape: ajouter_log(f"   {etape}")
            )
            toutes_annonces.extend(annonces_site)
            ajouter_log(f"✅  {scraper.nom} — {len(annonces_site)} annonce(s) récupérée(s)")
        except Exception as e:
            ajouter_log(f"❌  {scraper.nom} a échoué : {e}")
            logging.exception(f"Erreur critique scraper {scraper.nom}")

    ajouter_log(f"🔍  Déduplication et filtrage en cours…")
    resultat = dedupliquer_et_enrichir(toutes_annonces, criteres=criteres_ui)

    nb_nouvelles = sum(1 for a in resultat if a.get("nouveau"))
    ajouter_log(
        f"📊  {len(resultat)} annonce(s) retenue(s) "
        f"dont {nb_nouvelles} nouvelle(s)"
    )

    if resultat:
        ajouter_log("💾  Sauvegarde dans le fichier Excel…")
        sauvegarder_annonces(resultat)
        ajouter_log(f"✅  Excel mis à jour → {EXCEL_PATH}")

    ajouter_log("🏁  Recherche terminée !")
    st.session_state.logs = logs
    return resultat


def annonces_en_dataframe(annonces: list) -> pd.DataFrame:
    """Convertit la liste de dicts en DataFrame Pandas pour l'affichage."""
    if not annonces:
        return pd.DataFrame(columns=COLONNES_EXCEL)

    lignes = []
    for a in annonces:
        lignes.append({
            "Commune":      a.get("commune") or "",
            "Type":         a.get("type") or "",
            "Loyer (€)":    a.get("loyer"),
            "Charges":      a.get("charges") or "",
            "Chambres":     a.get("chambres"),
            "Surface (m²)": a.get("surface"),
            "DPE":          a.get("dpe") or "",
            "Lien":         a.get("lien") or "",
            "Date repérée": a.get("date_reperee") or "",
            "Source":       a.get("source") or "",
            "Nouveau":      "🆕 Oui" if a.get("nouveau") else "Non",
            "Score":        int(a.get("score") or 0),
        })

    return pd.DataFrame(lignes)


def dataframe_en_excel_bytes(df: pd.DataFrame) -> bytes:
    """Sérialise un DataFrame en bytes Excel pour le bouton de téléchargement."""
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Annonces Dinan")
    return buf.getvalue()


def appliquer_filtres(df: pd.DataFrame, commune_f: str, source_f: str,
                      loyer_max_f: int, chambres_min_f: int,
                      nouvelles_seulement: bool) -> pd.DataFrame:
    """Applique les filtres de la sidebar sur le DataFrame affiché."""
    if df.empty:
        return df

    if commune_f != "Toutes":
        df = df[df["Commune"].str.lower() == commune_f.lower()]

    if source_f != "Toutes":
        df = df[df["Source"] == source_f]

    if loyer_max_f:
        df = df[df["Loyer (€)"].isna() | (df["Loyer (€)"] <= loyer_max_f)]

    if chambres_min_f and chambres_min_f > 1:
        df = df[df["Chambres"].isna() | (df["Chambres"] >= chambres_min_f)]

    if nouvelles_seulement:
        df = df[df["Nouveau"].str.contains("Oui", na=False)]

    return df


# ---------------------------------------------------------------------------
# INTERFACE — En-tête
# ---------------------------------------------------------------------------

st.title("🏡 Locations Dinan — Bretagne")
st.caption("Aide à la recherche d'un logement pour la retraite dans la région de Dinan (22)")

# ---------------------------------------------------------------------------
# SIDEBAR — Paramètres de recherche
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Paramètres de recherche")

    st.subheader("Critères")
    loyer_max_ui = st.slider(
        "Loyer maximum (€/mois, CC)",
        min_value=400, max_value=1200,
        value=CRITERES["loyer_max"], step=50,
        help="Charges comprises (CC). Les annonces hors charges sont acceptées si le loyer est ≤ ce montant.",
    )
    chambres_min_ui = st.number_input(
        "Chambres minimum",
        min_value=1, max_value=6,
        value=CRITERES["chambres_min"],
    )
    inclure_appart_ui = st.checkbox(
        "Inclure les appartements",
        value=CRITERES["inclure_appartements"],
        help="Désactivé par défaut — seules les maisons sont recherchées.",
    )

    st.divider()
    st.subheader("Filtres sur les résultats affichés")

    communes_liste = sorted({
        c.title() for c in list(COMMUNES_PRIORITAIRES.keys()) + COMMUNES_RAYON
        if len(c) > 4
    })
    commune_filtre = st.selectbox("Commune", ["Toutes"] + communes_liste)

    source_filtre = st.selectbox(
        "Source",
        ["Toutes", "PAP.fr", "Ouest-France Immo"],
    )

    loyer_max_filtre = st.number_input(
        "Loyer affiché ≤ (€)",
        min_value=0, max_value=2000,
        value=loyer_max_ui, step=50,
    )

    chambres_min_filtre = st.number_input(
        "Chambres affichées ≥",
        min_value=0, max_value=6,
        value=0,
        help="0 = afficher tout",
    )

    nouvelles_seulement = st.checkbox("Nouvelles annonces uniquement", value=False)

    st.divider()
    st.caption(
        "ℹ️ **Bonnes pratiques** : délai 2–5 s entre requêtes, "
        "robots.txt respecté, user-agent réaliste."
    )

    # Affiche la date de dernière recherche
    if st.session_state.derniere_recherche:
        st.success(f"Dernière recherche : {st.session_state.derniere_recherche}")

# ---------------------------------------------------------------------------
# Corps principal — Bouton + état fichier
# ---------------------------------------------------------------------------
col_btn, col_info = st.columns([2, 1])

with col_btn:
    lancer = st.button("🔍  Lancer la recherche", type="primary", use_container_width=True)

with col_info:
    if os.path.exists(EXCEL_PATH):
        taille_ko = os.path.getsize(EXCEL_PATH) // 1024
        st.success(f"📄 Excel existant ({taille_ko} Ko)")
    else:
        st.info("Aucun fichier Excel — il sera créé lors de la première recherche.")

# ---------------------------------------------------------------------------
# Lancement du scraping
# ---------------------------------------------------------------------------
if lancer:
    criteres_ui = {
        "loyer_max": loyer_max_ui,
        "chambres_min": int(chambres_min_ui),
        "inclure_appartements": inclure_appart_ui,
    }

    st.divider()
    st.subheader("📡 Journal de scraping")
    placeholder_log = st.empty()

    with st.spinner("Scraping en cours — merci de patienter (peut prendre 1–3 min)…"):
        annonces = lancer_scraping(criteres_ui, placeholder_log)

    st.session_state.annonces = annonces
    st.session_state.derniere_recherche = datetime.now().strftime("%d/%m/%Y à %H:%M")

    nb_nouvelles = sum(1 for a in annonces if a.get("nouveau"))
    if annonces:
        st.success(
            f"✅ Recherche terminée : **{len(annonces)} annonce(s)** trouvée(s), "
            f"dont **{nb_nouvelles} nouvelle(s)**."
        )
    else:
        st.warning(
            "Aucune annonce ne correspond à vos critères. "
            "Vérifiez la connexion Internet ou élargissez les filtres."
        )

# ---------------------------------------------------------------------------
# Affichage des résultats
# ---------------------------------------------------------------------------
if st.session_state.annonces:
    df_base = annonces_en_dataframe(st.session_state.annonces)

    df_affiche = appliquer_filtres(
        df_base,
        commune_f=commune_filtre,
        source_f=source_filtre,
        loyer_max_f=loyer_max_filtre,
        chambres_min_f=int(chambres_min_filtre),
        nouvelles_seulement=nouvelles_seulement,
    )

    st.divider()

    # Métriques rapides
    c1, c2, c3, c4 = st.columns(4)
    nb_nouvelles_df = df_affiche["Nouveau"].str.contains("Oui", na=False).sum()
    loyer_moyen = df_affiche["Loyer (€)"].mean()
    score_moyen = df_affiche["Score"].mean()

    c1.metric("Annonces affichées", len(df_affiche))
    c2.metric("🆕 Nouvelles", int(nb_nouvelles_df))
    c3.metric("Loyer moyen", f"{loyer_moyen:.0f} €" if not pd.isna(loyer_moyen) else "N/A")
    c4.metric("Score moyen", f"{score_moyen:.0f}/100" if not pd.isna(score_moyen) else "N/A")

    st.subheader(f"📋 Annonces ({len(df_affiche)}) — triées par score décroissant")

    st.dataframe(
        df_affiche,
        use_container_width=True,
        height=560,
        hide_index=True,
        column_config={
            "Lien": st.column_config.LinkColumn(
                "Lien",
                display_text="Voir l'annonce →",
                width="medium",
            ),
            "Score": st.column_config.ProgressColumn(
                "Score",
                min_value=0,
                max_value=100,
                format="%d",
                width="small",
            ),
            "Loyer (€)": st.column_config.NumberColumn(
                "Loyer (€)",
                format="%.0f €",
                width="small",
            ),
            "Surface (m²)": st.column_config.NumberColumn(
                "Surface",
                format="%.0f m²",
                width="small",
            ),
            "Chambres": st.column_config.NumberColumn(
                "Ch.", width="small",
            ),
            "DPE": st.column_config.TextColumn("DPE", width="small"),
            "Nouveau": st.column_config.TextColumn("Nouveau", width="small"),
        },
    )

    # Téléchargement Excel
    excel_bytes = dataframe_en_excel_bytes(df_affiche)
    nom_fichier = f"locations_dinan_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"

    st.download_button(
        label="⬇️  Télécharger le tableau en Excel",
        data=excel_bytes,
        file_name=nom_fichier,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

else:
    if not lancer:
        st.info(
            "👆 Cliquez sur **Lancer la recherche** pour démarrer.\n\n"
            "Les annonces de maisons à louer dans la région de Dinan s'afficheront ici, "
            "triées par score de pertinence."
        )
