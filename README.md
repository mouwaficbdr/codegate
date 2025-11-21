# ⚡ CodeGate

**CodeGate** est un outil de productivité Linux innovant qui bloque vos applications distrayantes et vous oblige à résoudre un challenge de code pour y accéder.

> 🎯 **Objectif** : Améliorer votre discipline personnelle tout en développant vos compétences en programmation.

![CodeGate Challenge UI](assets/screenshots/challenge_ui.png)

---

## Fonctionnalités

### 🔒 Blocage Intelligent
- Surveillance continue des applications configurées
- Blocage instantané via `SIGSTOP` (sans terminer l'app)
- Détection rapide (0.3s) pour intercepter les lancements
- Protection anti-contournement avec watchdog

### 💻 Challenges de Code
- Problèmes algorithmiques variés
- Support multi-langages : **Python** • **JavaScript** • **PHP**
- Niveaux de difficulté : Facile, Moyen, Difficile, Mixte
- 200+ challenges intégrés
- Éditeur avec coloration syntaxique

![CodeGate Settings](assets/screenshots/main_settings.png)

### 🛡️ Robustesse
- **Watchdog** : Relance automatique si CodeGate est fermé
- **Protection config** : Détection de modifications via checksum SHA256
- **Démarrage auto** : S'active à chaque connexion
- **Logs détaillés** : Rotation automatique (5MB)

### 📊 Statistiques
- Blocages quotidiens et totaux
- Challenges résolus/échoués
- Taux de réussite
- Historique complet

### Interface Moderne
- Interface graphique PySide6
- Welcome wizard pour configuration initiale
- Sélection d'apps avec catégories
- Notifications système
- Recherche en temps réel

---

## 📋 Prérequis

- **OS** : Linux (testé sur Ubuntu/Debian)
- **Python** : 3.10+
- **Node.js** : Pour les challenges JavaScript (v14+ recommandé)
- **PHP** : Pour les challenges PHP (v7.4+ recommandé)
- **Environnement** : Desktop avec gestionnaire de fenêtres

> ℹ️ **Note** : Le script d'installation propose d'installer automatiquement Node.js et PHP s'ils sont absents. Vous pouvez aussi utiliser uniquement Python si vous préférez.

---

## 🚀 Installation

### Méthode automatique (recommandée)

```bash
# Cloner le repository
git clone https://github.com/mouwaficbdr/codegate.git
cd codegate

# Lancer l'installation
./install.sh
```

Le script va :
- ✅ Vérifier Python 3.10+
- ✅ Créer un environnement virtuel
- ✅ Installer les dépendances
- ✅ Configurer le démarrage automatique
- ✅ Créer les dossiers nécessaires

### Installation manuelle

```bash
# 1. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Copier le fichier autostart
mkdir -p ~/.config/autostart
cp codegate.desktop ~/.config/autostart/

# 4. Éditer le chemin dans codegate.desktop
nano ~/.config/autostart/codegate.desktop
# Remplacer /home/mouwaficbdr/Code/codegate par votre chemin
```

---

## Utilisation

### Premier lancement

Au premier démarrage, un wizard de configuration s'affiche pour vous guider :

<p align="center">
  <img src="assets/screenshots/onboarding_apps.png" width="32%" alt="Sélection Apps" />
  <img src="assets/screenshots/onboarding_difficulty.png" width="32%" alt="Difficulté" />
  <img src="assets/screenshots/onboarding_done.png" width="32%" alt="Résumé" />
</p>

1. **Bienvenue** : Présentation du concept
2. **Sélection apps** : Choisir les apps à bloquer
3. **Difficulté** : Niveau des challenges
4. **Résumé** : Vérification et validation

### Utilisation quotidienne

1. CodeGate démarre automatiquement au login
2. Les apps configurées sont surveillées
3. Si vous lancez une app bloquée :
   - ⏸️ L'app est mise en pause (SIGSTOP)
   - 📝 Un challenge s'affiche en plein écran
   - 💻 Résolvez le challenge
   - ✅ L'app est débloquée si succès

### Paramètres

Cliquez sur l'icône ⚙️ pour :
- Modifier les applications bloquées
- Changer la difficulté
- Ajouter des apps personnalisées
- Voir les statistiques

---

## 📁 Architecture

```
codegate/
├── src/
│   ├── main.py                   # Point d'entrée principal
│   ├── main_gui.py                # Interface graphique
│   ├── watchdog.py                # Protection anti-kill
│   ├── process_blocker.py         # Blocage des processus
│   ├── process_monitor.py         # Détection avancée
│   ├── config_protector.py        # Protection configuration
│   ├── code_runner.py             # Exécution du code utilisateur
│   ├── challenge_fetcher.py       # Récupération challenges
│   ├── notification_manager.py    # Notifications système
│   ├── logger.py                  # Logs centralisés
│   └── onboarding.py              # Wizard première utilisation
├── assets/
│   └── challenges.json            # Base de 200+ challenges
├── install.sh                     # Script d'installation
├── uninstall.sh                   # Script de désinstallation
├── run_codegate.sh                # Launcher watchdog
├── codegate.desktop               # Fichier autostart
└── config.json                    # Configuration utilisateur
```

---

## 🔧 Configuration avancée

### Fichier `config.json`

```json
{
    "blocked_apps": ["discord", "firefox", "steam"],
    "custom_apps": ["my-app"],
    "language": "fr",
    "difficulty_mode": "Mixed",
    "first_run": false
}
```

### Logs

Emplacement : `~/.local/share/codegate/logs/`
- `codegate.log` : Logs principaux (5MB rotation)
- `errors.log` : Erreurs uniquement
- `watchdog.log` : Logs du watchdog

### Statistiques

Fichier : `~/.local/share/codegate/stats.json`

---

## ❓ FAQ

**Q : CodeGate fonctionne-t-il hors ligne ?**  
R : Oui ! Tous les challenges sont stockés localement.

**Q : Puis-je désactiver temporairement CodeGate ?**  
R : Oui, via `pkill -f codegate`. Mais le watchdog le relancera après ~3s.

**Q : Comment désinstaller complètement ?**  
R : Exécutez `./uninstall.sh` qui nettoie tout.

**Q : Puis-je ajouter mes propres challenges ?**  
R : Oui, éditez `assets/challenges.json` (voir structure).

**Q : CodeGate nécessite-t-il sudo ?**  
R : Non pour l'utilisation. Optionnel pour l'installation système.

---

## Dépannage

### CodeGate ne démarre pas
```bash
# Vérifier les logs
cat ~/.local/share/codegate/logs/codegate.log

# Tester manuellement
./run_codegate.sh
```

### Les apps ne se bloquent pas
1. Vérifier que l'app est dans la liste
2. Vérifier le nom du processus : `ps aux | grep appname`
3. Consulter les logs pour les erreurs

### Erreur "Virtual environment not found"
```bash
# Recréer le venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Pour plus d'aide, consultez `docs/TROUBLESHOOTING.md`

---

## 🤝 Contribution

Les contributions sont bienvenues ! 

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

---

## 📄 Licence

MIT License - Voir le fichier `LICENSE` pour les détails. (Si j'ai pensé à le mettre mdr)

---

**Made with ⚡ for focused devs(lol)**

