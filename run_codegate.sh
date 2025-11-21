#!/bin/bash
# Script de lancement de CodeGate
# Ce script démarre le watchdog qui surveille et relance CodeGate

# Obtenir le répertoire du script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Chemin vers le venv Python
VENV_PYTHON="$SCRIPT_DIR/venv/bin/python3"

# Vérifier que le venv existe
if [ ! -f "$VENV_PYTHON" ]; then
    echo "ERROR: Virtual environment not found at $VENV_PYTHON"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Créer le dossier de logs
mkdir -p "$HOME/.local/share/codegate/logs"

# Fichier de log pour ce script
LOG_FILE="$HOME/.local/share/codegate/logs/launcher.log"

# Logger le démarrage
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting CodeGate via watchdog..." >> "$LOG_FILE"

# Lancer le watchdog qui surveillera main.py
"$VENV_PYTHON" "$SCRIPT_DIR/src/watchdog.py" >> "$LOG_FILE" 2>&1 &

# Sauvegarder le PID du watchdog
WATCHDOG_PID=$!
echo $WATCHDOG_PID > "$HOME/.local/share/codegate/watchdog.pid"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Watchdog started with PID $WATCHDOG_PID" >> "$LOG_FILE"

# Message de succès
notify-send "CodeGate" "CodeGate watchdog started successfully" --icon=security-high 2>/dev/null || true

exit 0
