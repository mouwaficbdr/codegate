# ❓ FAQ – Frequently Asked Questions

## Installation & Setup

### Q: What are the system requirements?

**A:**

* Linux (Ubuntu, Debian, Fedora, Arch, etc.)
* Python 3.10 or higher
* **Node.js** (v14+) for JavaScript challenges
* **PHP** (v7.4+) for PHP challenges
* Desktop environment (GNOME, KDE, XFCE, etc.)
* 100 MB of disk space

### Q: Are Node.js and PHP required?

**A:** No! If you only have Python installed, you can still:

* Use CodeGate
* Solve **Python-only** challenges
* The `install.sh` script automatically detects missing languages and offers to install them

**Manual installation:**

```bash
# Node.js (Ubuntu/Debian)
sudo apt install nodejs

# PHP (Ubuntu/Debian)
sudo apt install php-cli
```

### Q: Does CodeGate work without internet access?

**A:** Yes! CodeGate is fully offline. All 200+ challenges are embedded in `assets/challenges.json`.

### Q: Can I install CodeGate without sudo/root?

**A:** Yes! The default installation occurs entirely in user space (`~/.local` and `~/.config`).
Sudo is only needed for an optional system-wide install.

### Q: How do I update CodeGate?

**A:**

```bash
cd /path/to/codegate
git pull origin main
./install.sh  # Reinstall with new updates
```

---

## Usage

### Q: How do I block a new application?

**A:**

1. Click the ⚙️ (settings) icon
2. Open the "Blocked Apps" tab
3. Search for the app or click "+ Add application"
4. Check the app and save

### Q: What process name should I use for an app?

**A:** Use `ps aux | grep appname` to find the exact name. Examples:

* Discord → `discord` or `Discord`
* VS Code → `code`
* Google Chrome → `chrome`
* Firefox → `firefox`

### Q: Can I temporarily disable CodeGate?

**A:** Yes, several methods:

```bash
# Stop both the watchdog AND the main app
pkill -f watchdog && pkill -f "python.*main.py"

# Disable autostart (until next reboot)
rm ~/.config/autostart/codegate.desktop
```

Note: If you kill only the main app, the watchdog will relaunch it after ~3 seconds.

### Q: How do I change the challenge difficulty?

**A:**

1. Settings ⚙️ → "General"
2. Choose the level: Easy, Medium, Hard, or Mixed
3. Save

---

## Common Issues

### Q: CodeGate is blocking an app I didn’t configure

**A:** Check your `config.json`. Make sure `blocked_apps` contains only what you want.
Some process names are generic (ex: `code` affects VS Code *and* other binaries named "code").

### Q: An app launches then gets blocked 1 second later

**A:** Normal behavior. CodeGate scans every 0.3s.
For instant interception, the app must launch after CodeGate is running.

### Q: The challenge window doesn’t appear fullscreen

**A:**

* Check your window manager’s fullscreen permissions
* Some WMs (i3, awesome) need extra config
* You can switch to windowed mode in settings

### Q: My code is correct but the test fails

**A:**

1. Check exact output (spaces, types, formatting)
2. Re-read the problem constraints
3. Test your code separately (Python/JS/PHP)
4. Check logs: `~/.local/share/codegate/logs/codegate.log`

---

## Challenges

### Q: Can I add my own challenges?

**A:** Yes! Edit `assets/challenges.json`. Format:

```json
{
    "title": "My Challenge",
    "description": "Problem description",
    "difficulty": "Easy",
    "category": "Arrays",
    "templates": {
        "python": "def solution(x):\n    # Your code\n    pass",
        "javascript": "function solution(x) {\n    // Your code\n}",
        "php": "function solution($x) {\n    // Your code\n}"
    },
    "tests": [
        {"input": [5], "expected": 25},
        {"input": [10], "expected": 100}
    ],
    "types": {}
}
```

### Q: Is there a time limit to solve a challenge?

**A:** No. Take your time!
But the app stays blocked until you succeed.

### Q: Can I choose the programming language?

**A:** Yes! The selector in the top-right lets you switch between Python, JavaScript, and PHP.

---

## Security & Privacy

### Q: Is my code sent anywhere?

**A:** No. CodeGate is fully local.
No network requests. Your code never leaves your machine.

### Q: Can someone easily bypass CodeGate?

**A:** CodeGate includes protections:

* Watchdog auto-restart
* Config checksum protection
* Tampering detection

But **it’s not enterprise parental control**.
A technical user can bypass it (kill -9, edit source, etc.).
The goal is **self-discipline**, not enforcement.

### Q: Can CodeGate damage my applications?

**A:** No.
It uses `SIGSTOP`/`SIGCONT`, standard POSIX pause/resume signals.
It never modifies application files.

---

## Performance

### Q: Does CodeGate use many resources?

**A:**

* CPU: ~0.1–0.5% idle (scan every 0.3s)
* RAM: ~50–80 MB (Python + PySide6)
* Disk: Logs capped at 5MB with rotation

### Q: Does it slow down system startup?

**A:** Minimal impact.
Autostart adds ~2–3 seconds to login.

---

## Data & Stats

### Q: Where is my data stored?

**A:**

* Config: `/path/to/codegate/config.json`
* Logs: `~/.local/share/codegate/logs/`
* Stats: `~/.local/share/codegate/stats.json`

### Q: How do I reset my stats?

**A:**

```bash
rm ~/.local/share/codegate/stats.json
```

They’ll be recreated at next launch.

### Q: Can I export my stats?

**A:** Yes. `stats.json` is plain JSON.
You can copy it, parse it, or generate custom graphs.

---

## Uninstallation

### Q: How do I uninstall CodeGate completely?

**A:**

```bash
cd /path/to/codegate
./uninstall.sh
```

The script lets you choose whether to keep logs and config.

### Q: What if I just delete the folder?

**A:** Apps will work normally, *but*:

* Autostart entry remains (`~/.config/autostart/codegate.desktop`)
* Logs remain in `~/.local/share/codegate/`

Use `uninstall.sh` for a clean removal.

---

## Other

### Q: Does CodeGate support Wayland?

**A:** Yes! PySide6 works on both X11 and Wayland.

### Q: Can multiple Linux users use CodeGate?

**A:** Yes, each user has an independent instance.

### Q: Does CodeGate work on a server (headless)?

**A:** No. A graphical environment is required.

### Q: Where do I report bugs?

**A:** GitHub Issues: [https://github.com/mouwaficbdr/codegate/issues](https://github.com/mouwaficbdr/codegate/issues)

---

**More questions? Check `docs/TROUBLESHOOTING.md` or open an issue!**
