#!/usr/bin/env bash
# Lancement de l'application — Linux / macOS
# Double-clic sur ce fichier ou : bash launch.sh

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Crée le virtualenv si absent
if [ ! -d ".venv" ]; then
    echo "Création du virtualenv Python…"
    python3 -m venv .venv
fi

# Active le virtualenv
source .venv/bin/activate

# Installe/met à jour les dépendances
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo "=============================="
echo "  Locations Dinan — démarrage"
echo "  http://localhost:8501"
echo "=============================="
echo ""

# Ouvre le navigateur automatiquement (si disponible)
if command -v xdg-open &>/dev/null; then
    sleep 2 && xdg-open "http://localhost:8501" &
elif command -v open &>/dev/null; then   # macOS
    sleep 2 && open "http://localhost:8501" &
fi

streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
