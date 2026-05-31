@echo off
REM Lancement de l'application — Windows
REM Double-clic sur ce fichier

cd /d "%~dp0"

REM Crée le virtualenv si absent
if not exist ".venv" (
    echo Creation du virtualenv Python...
    python -m venv .venv
)

REM Active le virtualenv
call .venv\Scripts\activate.bat

REM Installe/met a jour les dependances
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo.
echo ==============================
echo   Locations Dinan - demarrage
echo   http://localhost:8501
echo ==============================
echo.

REM Ouvre le navigateur apres 3 secondes
start "" /b cmd /c "timeout /t 3 >nul && start http://localhost:8501"

streamlit run app.py --server.port 8501 --browser.gatherUsageStats false
pause
