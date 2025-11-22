# 🔧 Troubleshooting Guide - CodeGate

This guide helps you diagnose and fix common issues with CodeGate.

---

## 🚫 Startup Issues

### CodeGate doesn’t start

#### Symptoms

* No window appears
* No startup notification
* No process in `ps aux`

#### Solutions

**1. Check the logs**

```bash
cat ~/.local/share/codegate/logs/codegate.log
cat ~/.local/share/codegate/logs/errors.log
```

**2. Try starting it manually**

```bash
cd /path/to/codegate
./run_codegate.sh
```

Watch the error messages.

**3. Check the virtual environment**

```bash
ls -la venv/
# If missing or corrupted:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Check permissions**

```bash
chmod +x run_codegate.sh
ls -la run_codegate.sh  # Should show -rwxr-xr-x
```

**5. Missing dependencies**

```bash
source venv/bin/activate
python3 -c "import PySide6, psutil, requests"
# If error, reinstall:
pip install --force-reinstall PySide6 psutil requests
```

**6. Missing Node.js or PHP**
If JS or PHP challenges don’t work:

```bash
# Check Node.js
node --version
# If missing:
sudo apt install nodejs

# Check PHP
php --version
# If missing:
sudo apt install php-cli
```

---

### Watchdog doesn’t start

#### Symptom

```
ERROR: Cannot find main.py at /path/to/codegate/src/main.py
```

#### Solution

```bash
# Ensure main.py exists
ls -la src/main.py

# Check the path in watchdog.py
grep "main_script" src/watchdog.py
```

---

### Error: “Python version too old”

#### Symptom

```
Python 3.10+ required, but found 3.8.x
```

#### Solution

```bash
sudo apt update
sudo apt install python3.11 python3.11-venv

# Recreate venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🔒 Blocking Issues

### Applications are not blocked

#### Diagnostics

**1. Check that CodeGate is running**

```bash
ps aux | grep -e watchdog -e "python.*main.py"
```

You should see 2 processes.

**2. Check the configuration**

```bash
cat config.json
```

**3. Check the process name**

```bash
ps aux | grep discord  # Replace with your app
```

Examples:

* Discord → `discord` or `Discord`
* Chrome → `chrome`
* VS Code → `code`

**4. Test manually**

```bash
source venv/bin/activate
python3 -c "
from src.process_blocker import ProcessBlocker
blocker = ProcessBlocker(['discord'])
blocker.start()
import time
time.sleep(30)
"
```

#### Solutions

**Incorrect process name**

```bash
ps aux | grep -i app_name
nano config.json
```

**Permission issue**

```bash
whoami
ps aux | grep discord | grep $(whoami)
```

---

### App opens then gets blocked after 1 second

#### Expected behavior

CodeGate scans every 0.3s — slight delay is normal.

#### Faster scan (advanced)

```python
time.sleep(0.1)
```

---

### CodeGate blocks too many apps

#### Cause

Process name too generic (example: `"code"`).

#### Solution

Be more specific:

```bash
ps aux | grep code
```

---

## 💻 Interface Issues

### Challenge window is not fullscreen

**i3wm fix**

```bash
for_window [class="Python3"] fullscreen enable
```

Other WMs: adjust window settings.

---

### Code editor shows broken characters

```bash
sudo apt install fonts-dejavu fonts-liberation
fc-cache -fv
```

---

### Notifications don’t appear

```bash
notify-send "Test" "Message test"

# If missing:
sudo apt install libnotify-bin

# GNOME
sudo apt install notification-daemon

# KDE
sudo apt install plasma-workspace
```

---

## ⚡ Performance Issues

### High CPU usage

#### Diagnose

```bash
top -p $(pgrep -f codegate)
```

#### Solutions

**Constant high CPU (>5%)**

```bash
tail -f ~/.local/share/codegate/logs/codegate.log
nano src/process_blocker.py
# Increase interval:
time.sleep(0.5)
```

**Too many open files**

```bash
lsof -p $(pgrep -f main.py) | wc -l
```

---

### High RAM usage

Check:

```bash
ps aux | grep python | grep main.py
```

Normal: 50–100 MB
Problem: >200 MB

Solution:

```bash
rm ~/.local/share/codegate/logs/*.log.*
pkill -f watchdog.py
./run_codegate.sh
```

---

## 🗂️ Configuration Issues

### “Configuration file has been modified!”

#### Cause

SHA256 checksum mismatch.

#### Solution (intended)

```bash
python3 -c "
from src.config_protector import ConfigProtector
import json
protector = ConfigProtector('config.json')
with open('config.json') as f:
    config = json.load(f)
protector.save_config(config)
print('✓ Checksum updated')
"
```

---

### Corrupted config.json

```bash
mv config.json config.json.broken
cp config.json.backup config.json

# Or recreate
cat > config.json << 'EOF'
{
    "blocked_apps": [],
    "custom_apps": [],
    "language": "en",
    "difficulty_mode": "Mixed",
    "first_run": true
}
EOF
```

---

## 🔄 Autostart Issues

### CodeGate doesn’t start on login

Check:

```bash
ls -la ~/.config/autostart/codegate.desktop
cat ~/.config/autostart/codegate.desktop
```

Fix:

```bash
cat > ~/.config/autostart/codegate.desktop << EOF
[Desktop Entry]
Type=Application
Name=CodeGate
Exec=/path/to/codegate/run_codegate.sh
Terminal=false
X-GNOME-Autostart-enabled=true
EOF
```

Session logs:

```bash
journalctl --user -b | grep codegate
cat ~/.local/share/codegate/logs/launcher.log
```

---

## 🧪 Challenge Issues

### “Module not found” during execution

Python sandbox only allows standard library.

Allowed:

* `math`, `itertools`, `collections`, `functools`

Not allowed:

* `numpy`, `pandas`, `requests`

---

### JavaScript challenges don’t work

```
ERROR: node: command not found
```

Install Node.js depending on your distro.

---

### PHP challenges don’t work

```
ERROR: php: command not found
```

Install `php-cli` depending on your distro.

---

### Tests fail but code looks correct

Add debug prints:

```python
print(f"DEBUG: input={arr}, result={result}")
```

Check:

```bash
cat ~/.local/share/codegate/logs/codegate.log | grep DEBUG
```

---

## 🆘 Full Reset

```bash
pkill -9 -f codegate
pkill -9 -f watchdog

cp config.json ~/config.json.backup

rm -rf ~/.local/share/codegate/
rm ~/.config/autostart/codegate.desktop
rm config.json .config_checksum config.json.backup

./install.sh
```

---

## 📞 Get Help

1. **Check logs first**

   ```bash
   tail -100 ~/.local/share/codegate/logs/*.log
   ```

2. Check GitHub Issues

3. Open a new issue with:

   * Python version
   * Linux distro
   * Logs
   * Steps to reproduce

4. Verbose mode:

   ```bash
   # logger.py line 24
   verbose=True
   ```

---

**Happy debugging! 🔧**
