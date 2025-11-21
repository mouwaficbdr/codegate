# 🔧 Guide de Dépannage - CodeGate

Ce guide vous aide à résoudre les problèmes courants avec CodeGate.

---

## 🚫 Problèmes de Démarrage

### CodeGate ne démarre pas

#### Symptômes
- Aucune fenêtre ne s'affiche
- Pas de notification de démarrage
- Processus absent de `ps aux`

#### Solutions

**1. Vérifier les logs**
```bash
cat ~/.local/share/codegate/logs/codegate.log
cat ~/.local/share/codegate/logs/errors.log
```

**2. Tester le démarrage manuel**
```bash
cd /path/to/codegate
./run_codegate.sh
```
Observez les messages d'erreur.

**3. Vérifier l'environnement virtuel**
```bash
ls -la venv/
# Si absent ou corrompu :
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Vérifier les permissions**
```bash
chmod +x run_codegate.sh
ls -la run_codegate.sh  # Doit afficher -rwxr-xr-x
```

**5. Dépendances manquantes**
```bash
source venv/bin/activate
python3 -c "import PySide6, psutil, requests"
# Si erreur, réinstaller :
pip install --force-reinstall PySide6 psutil requests
```

---

### Watchdog ne démarre pas

#### Symptôme
```
ERROR: Cannot find main.py at /path/to/codegate/src/main.py
```

#### Solution
```bash
# Vérifier que main.py existe
ls -la src/main.py

# Vérifier le chemin dans watchdog.py
grep "main_script" src/watchdog.py
```

---

### Erreur "Python version too old"

#### Symptôme
```
Python 3.10+ required, but found 3.8.x
```

#### Solution
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv

# Puis recréer le venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔒 Problèmes de Blocage

### Les applications ne se bloquent pas

#### Diagnostic

**1. Vérifier que CodeGate tourne**
```bash
ps aux | grep -e watchdog -e "python.*main.py"
```
Vous devriez voir 2 processus.

**2. Vérifier la configuration**
```bash
cat config.json
```
Vérifiez que `blocked_apps` contient bien vos applications.

**3. Vérifier le nom du processus**
```bash
# Lancer l'app à bloquer, puis :
ps aux | grep discord  # Remplacer discord par votre app
```
Le nom exact du processus peut différer :
- Discord → `discord` ou `Discord`
- Chrome → `chrome` pas `google-chrome`
- VS Code → `code`

**4. Tester manuellement**
```bash
# Dans un terminal avec venv activé
source venv/bin/activate
python3 -c "
from src.process_blocker import ProcessBlocker
blocker = ProcessBlocker(['discord'])
blocker.start()
import time
time.sleep(30)  # Lancer Discord pendant ce temps
"
```

#### Solutions

**Problème : Nom de processus incorrect**
```bash
# Trouver le bon nom
ps aux | grep -i nom_app

# Mettre à jour config.json
nano config.json
# Modifier blocked_apps avec le nom exact
```

**Problème : Permissions**
```bash
# CodeGate ne peut bloquer que vos propres processus
whoami  # Noter votre nom d'utilisateur
ps aux | grep discord | grep $(whoami)  # L'app doit apparaître
```

---

### L'application se lance puis se bloque après 1 seconde

#### C'est normal !
CodeGate scanne toutes les 0.3s. Il y a un délai entre le lancement et la détection.

#### Pour améliorer (avancé)
Modifier `src/process_blocker.py` ligne 33 :
```python
time.sleep(0.1)  # Au lieu de 0.3
```
*Note : Augmente légèrement l'utilisation CPU*

---

### CodeGate bloque trop d'applications

#### Symptôme
Des apps non souhaitées sont bloquées.

#### Cause
Nom de processus trop générique. Ex: `"code"` bloque VS Code mais aussi tout binaire nommé "code".

#### Solution
```bash
# Être plus spécifique
# Au lieu de "code", utiliser le chemin complet ou un nom unique
ps aux | grep code  # Voir tous les processus "code"

# Option 1 : Retirer de blocked_apps
# Option 2 : Utiliser process_monitor.py avec chemins exacts (avancé)
```

---

## 💻 Problèmes d'Interface

### La fenêtre challenge ne s'affiche pas en plein écran

#### Solution pour i3wm
```bash
# Ajouter à ~/.config/i3/config
for_window [class="Python3"] fullscreen enable
```

#### Solution pour autres WM
Vérifier les paramètres de gestion des fenêtres de votre environnement.

---

### L'éditeur de code affiche mal les caractères

#### Solution
```bash
# Installer les polices
sudo apt install fonts-dejavu fonts-liberation
fc-cache -fv
```

---

### Les notifications ne s'affichent pas

#### Solution
```bash
# Vérifier notify-send
notify-send "Test" "Message de test"

# Si erreur, installer
sudo apt install libnotify-bin

# GNOME
sudo apt install notification-daemon

# KDE
sudo apt install plasma-workspace
```

---

## ⚡ Problèmes de Performance

### CodeGate consomme trop de CPU

#### Diagnostic
```bash
top -p $(pgrep -f codegate)
```

#### Solutions

**CPU élevé en continu (>5%)**
```bash
# Vérifier les logs pour des loops
tail -f ~/.local/share/codegate/logs/codegate.log

# Augmenter l'intervalle de scan
nano src/process_blocker.py
# Ligne 33 : time.sleep(0.5)  # Au lieu de 0.3
```

**Trop de fichiers ouverts**
```bash
lsof -p $(pgrep -f main.py) | wc -l
# Si > 1000, il y a un leak
```

---

### CodeGate utilise trop de RAM

#### Vérifier
```bash
ps aux | grep python | grep main.py
# Colonne RSS = RAM en KB
```

#### Normal : 50-100 MB
#### Problème : > 200 MB

#### Solution
```bash
# Nettoyer les logs
rm ~/.local/share/codegate/logs/*.log.*

# Redémarrez CodeGate
pkill -f watchdog.py
./run_codegate.sh
```

---

## 🗂️ Problèmes de Configuration

### "Configuration file has been modified!"

#### Cause
Le checksum SHA256 ne correspond pas. Modification manuelle détectée.

#### Solution intentionnelle
```bash
# Si vous avez modifié volontairement :
python3 -c "
from src.config_protector import ConfigProtector
import json

protector = ConfigProtector('config.json')

# Charger et valider votre config
with open('config.json') as f:
    config = json.load(f)

# Recalculer le checksum
protector.save_config(config)
print('✓ Checksum updated')
"
```

---

### Config.json corrompu

#### Symptôme
```
JSON Decode Error
```

#### Solution
```bash
# Backup de l'ancien
mv config.json config.json.broken

# Restaurer depuis backup si existe
cp config.json.backup config.json

# Ou créer nouveau
cat > config.json << 'EOF'
{
    "blocked_apps": [],
    "custom_apps": [],
    "language": "fr",
    "difficulty_mode": "Mixed",
    "first_run": true
}
EOF
```

---

## 🔄 Problèmes d'Autostart

### CodeGate ne démarre pas au login

#### Vérifier l'autostart
```bash
ls -la ~/.config/autostart/codegate.desktop
cat ~/.config/autostart/codegate.desktop
```

#### Solution
```bash
# Recréer le fichier
cat > ~/.config/autostart/codegate.desktop << EOF
[Desktop Entry]
Type=Application
Name=CodeGate
Exec=/path/to/codegate/run_codegate.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

# Remplacer /path/to/codegate par votre chemin réel
```

#### Vérifier les logs de session
```bash
# GNOME
journalctl --user -b | grep codegate

# Consulter les logs de démarrage
cat ~/.local/share/codegate/logs/launcher.log
```

---

## 🧪 Problèmes de Challenges

### "Module not found" lors de l'exécution du code

#### Python
L'environnement d'exécution est isolé. Seuls les modules standard sont disponibles.

#### Solution
Utilisez uniquement la bibliothèque standard :
- ✅ `math`, `collections`, `itertools`, `functools`
- ❌ `numpy`, `pandas`, `requests`

---

### Tests échouent mais le code semble correct

#### Debug
Ajoutez des prints :
```python
def solution(arr):
    result = sum(arr)
    print(f"DEBUG: input={arr}, result={result}")  # Visible dans les logs
    return result
```

Consultez ensuite :
```bash
cat ~/.local/share/codegate/logs/codegate.log | grep DEBUG
```

---

## 🆘 Réinitialisation Complète

### Si rien ne fonctionne

```bash
# 1. Tuer tous les processus
pkill -9 -f codegate
pkill -9 -f watchdog

# 2. Sauvegarder la config si importante
cp config.json ~/config.json.backup

# 3. Nettoyer tout
rm -rf ~/.local/share/codegate/
rm ~/.config/autostart/codegate.desktop
rm config.json .config_checksum config.json.backup

# 4. Réinstaller
./install.sh
```

---

## 📞 Obtenir de l'Aide

Si ce guide ne résout pas votre problème :

1. **Consultez les logs** : Toujours commencer par là
   ```bash
   tail -100 ~/.local/share/codegate/logs/*.log
   ```

2. **Recherchez sur GitHub Issues** :
   https://github.com/mouwaficbdr/codegate/issues

3. **Ouvrez une nouvelle issue** avec :
   - Version de Python (`python3 --version`)
   - Distribution Linux (`lsb_release -a`)
   - Logs pertinents
   - Steps pour reproduire le problème

4. **Mode verbeux** pour diagnostic :
   ```bash
   # Modifier logger.py ligne 24
   verbose=True  # Force mode verbose
   ```

---

**Bon dépannage ! 🔧**
