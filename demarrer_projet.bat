@echo off
setlocal

title Demarrage PFA - Location de Voitures
cd /d "%~dp0"

echo ================================================
echo   Demarrage du projet PFA - Location de Voitures
echo ================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Python n'est pas disponible dans le PATH.
    echo Installez Python ou ajoutez-le au PATH, puis relancez ce fichier.
    goto fin_erreur
)

echo [1/5] Verification de Python...
python --version
echo.

echo [2/5] Verification de Django et des dependances...
python -c "import django" >nul 2>nul
if errorlevel 1 (
    echo Django n'est pas installe. Installation depuis requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [ERREUR] Installation des dependances impossible.
        goto fin_erreur
    )
) else (
    echo Django est deja installe.
)
echo.

echo [3/5] Verification du projet Django...
python manage.py check
if errorlevel 1 (
    echo [ERREUR] Le projet Django contient une erreur de configuration.
    goto fin_erreur
)
echo.

echo [4/5] Application des migrations...
python manage.py migrate
if errorlevel 1 (
    echo [ERREUR] Les migrations ont echoue.
    goto fin_erreur
)
echo.

echo [5/5] Ouverture du navigateur et lancement du serveur...
echo Adresse: http://127.0.0.1:8000/
echo.
start "" powershell -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://127.0.0.1:8000/'"

python manage.py runserver 127.0.0.1:8000

echo.
echo Le serveur Django s'est arrete.
pause
exit /b 0

:fin_erreur
echo.
echo La fenetre reste ouverte pour lire l'erreur.
pause
exit /b 1
