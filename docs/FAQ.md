# ❓ FAQ - Questions Fréquentes

## Installation et Configuration

### Q: Quels sont les prérequis système ?
**R:** 
- Linux (Ubuntu, Debian, Fedora, Arch, etc.)
- Python 3.10 ou supérieur
- Environnement desktop (GNOME, KDE, XFCE, etc.)
- 100 MB d'espace disque

### Q: CodeGate fonctionne-t-il sans connexion internet ?
**R:** Oui ! CodeGate est 100% fonctionnel hors ligne. Tous les 200+ challenges sont embarqués dans `assets/challenges.json`.

### Q: Puis-je installer CodeGate sans sudo/root ?
**R:** Oui ! L'installation standard se fait entièrement en espace utilisateur (`~/.local` et `~/.config`). Sudo n'est nécessaire que pour une installation système optionnelle.

### Q: Comment mettre à jour CodeGate ?
**R:**
```bash
cd /path/to/codegate
git pull origin main
./install.sh  # Réinstaller avec les nouvelles versions
```

---

## Utilisation

### Q: Comment bloquer une nouvelle application ?
**R:** 
1. Cliquez sur l'icône ⚙️ (paramètres) dans l'interface
2. Onglet "Blocked Apps"
3. Recherchez l'app ou cliquez sur "+ Ajouter une application"
4. Cochez l'app et sauvegardez

### Q: Quel nom de processus utiliser pour une application ?
**R:** Utilisez la commande `ps aux | grep nomapp` pour trouver le nom exact. Exemples :
- Discord → `discord` ou `Discord`
- VS Code → `code`
- Google Chrome → `chrome`
- Firefox → `firefox`

### Q: Puis-je désactiver temporairement CodeGate ?
**R:** Oui, plusieurs méthodes :
```bash
# Arrêter le watchdog ET l'app principale
pkill -f watchdog && pkill -f "python.*main.py"

# Désactiver l'autostart (jusqu'au prochain reboot)
rm ~/.config/autostart/codegate.desktop
```
Note : Le watchdog relancera CodeGate après ~3 secondes si tué seul.

### Q: Comment changer la difficulté des challenges ?
**R:**
1. Paramètres ⚙️ → Onglet "General"
2. Sélectionnez le niveau : Easy, Medium, Hard, ou Mixed
3. Sauvegardez

---

## Problèmes Courants

### Q: CodeGate bloque une app que je n'ai pas configurée
**R:** Vérifiez votre `config.json`. Assurez-vous que `blocked_apps` ne contient que les apps souhaitées. Il peut y avoir des noms de processus similaires (ex: `code` bloque VS Code mais aussi d'autres binaires nommés "code").

### Q: Une app se lance puis se bloque 1 seconde après
**R:** C'est normal ! CodeGate détecte l'app toutes les 0.3s. Pour une interception instantanée, l'app doit être lancée après que CodeGate soit actif.

### Q: Le challenge ne s'affiche pas en plein écran
**R:** 
- Vérifiez que votre gestionnaire de fenêtres autorise le fullscreen
- Certains window managers (i3, awesome) nécessitent une configuration spéciale
- Essayez mode fenêtré via les paramètres

### Q: Mon code est correct mais le test échoue
**R:**
1. Vérifiez la sortie exacte (espaces, types de données)
2. Lisez attentivement les contraintes du problème
3. Testez votre code dans un environnement Python/JS/PHP séparé
4. Consultez les logs : `~/.local/share/codegate/logs/codegate.log`

---

## Challenges

### Q: Puis-je ajouter mes propres challenges ?
**R:** Oui ! Éditez `assets/challenges.json`. Format :
```json
{
    "title": "Mon Challenge",
    "description": "Description du problème",
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

### Q: Y a-t-il une limite de temps pour résoudre un challenge ?
**R:** Non, prenez votre temps ! Mais les applications restent bloquées tant que vous n'avez pas résolu.

### Q: Puis-je choisir le langage de programmation ?
**R:** Oui ! Le sélecteur en haut à droite de l'interface permet de choisir entre Python, JavaScript et PHP.

---

## Sécurité et Confidentialité

### Q: Mon code est-il envoyé quelque part ?
**R:** Non ! CodeGate fonctionne 100% localement. Aucune connexion réseau n'est effectuée. Le code que vous écrivez reste sur votre machine.

### Q: Quelqu'un peut-il contourner CodeGate facilement ?
**R:** CodeGate dispose de protections :
- Watchdog qui relance l'app si tuée
- Protection du fichier config avec checksum
- Détection de modifications

Mais **ce n'est pas un système de contrôle parental** niveau enterprise. Un utilisateur déterminé avec connaissances techniques peut le contourner (kill -9, éditer le code source, etc.). L'objectif est la **discipline personnelle**, pas le blocage forcé.

### Q: CodeGate peut-il endommager mes applications ?
**R:** Non. CodeGate utilise `SIGSTOP`/`SIGCONT` qui sont des signaux standards POSIX pour pause/reprise. Aucune modification des fichiers d'application.

---

## Performance

### Q: CodeGate consomme-t-il beaucoup de ressources ?
**R:**
- CPU : ~0.1-0.5% en idle (scan toutes les 0.3s)
- RAM : ~50-80 MB (Python + PySide6)
- Disque : Logs limités à 5MB avec rotation

### Q: CodeGate ralentit-il le démarrage du système ?
**R:** Impact minimal. Le démarrage automatique ajoute ~2-3 secondes au login.

---

## Données et Statistiques

### Q: Où sont stockées mes données ?
**R:**
- Configuration : `/path/to/codegate/config.json`
- Logs : `~/.local/share/codegate/logs/`
- Statistiques : `~/.local/share/codegate/stats.json`

### Q: Comment réinitialiser mes statistiques ?
**R:**
```bash
rm ~/.local/share/codegate/stats.json
```
Elles seront recréées au prochain lancement.

### Q: Puis-je exporter mes statistiques ?
**R:** Oui, le fichier `stats.json` est au format JSON lisible. Vous pouvez le copier, le parser, ou créer vos propres graphiques.

---

## Désinstallation

### Q: Comment désinstaller complètement CodeGate ?
**R:**
```bash
cd /path/to/codegate
./uninstall.sh
```
Le script propose de garder les logs et la config si souhaité.

### Q: Que se passe-t-il si je supprime juste le dossier ?
**R:** Les apps bloquées resteront fonctionnelles. Mais :
- L'autostart restera dans `~/.config/autostart/codegate.desktop`
- Les logs resteront dans `~/.local/share/codegate/`

Utilisez `uninstall.sh` pour un nettoyage complet.

---

## Autres

### Q: CodeGate supporte-t-il Wayland ?
**R:** Oui ! PySide6 fonctionne sous X11 et Wayland.

### Q: Puis-je utiliser CodeGate avec plusieurs utilisateurs ?
**R:** Oui, chaque utilisateur Linux a sa propre instance indépendante.

### Q: CodeGate fonctionne-t-il sur serveur (headless) ?
**R:** Non, CodeGate nécessite un environnement graphique (GUI).

### Q: Où rapporter des bugs ?
**R:** GitHub Issues : https://github.com/mouwaficbdr/codegate/issues

---

**Des questions ? Consultez aussi `docs/TROUBLESHOOTING.md` ou ouvrez une issue !**
