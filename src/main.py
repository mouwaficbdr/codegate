import sys
import json
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot

from src.process_blocker import ProcessBlocker
from src.challenge_fetcher import ChallengeFetcher
from src.main_gui import OverlayWindow
from src.config_protector import ConfigProtector
from src.logger import get_logger
from src.notification_manager import NotificationManager
from src.onboarding import OnboardingWizard


class SignalBridge(QObject):
    request_overlay = Signal()


def main():
    app = QApplication(sys.argv)
    
    # Initialize logger (verbose mode can be enabled here)
    logger = get_logger("CodeGate", verbose=False)
    logger.info("="*50)
    logger.info("CodeGate starting...")
    
    # Initialize notification manager
    notifier = NotificationManager()
    
    # Configuration avec protection
    config_path = "config.json"
    protector = ConfigProtector(config_path)
    
    # Configuration par défaut
    default_config = {
        "blocked_apps": [],
        "custom_apps": [],
        "language": "fr",
        "difficulty_mode": "Mixed",
        "first_run": True
    }
    
    # Charger la config (avec vérification intégrité)
    try:
        config = protector.load_config(default_config)
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        config = default_config
        protector.save_config(config)
    
    # --- FIRST RUN: Onboarding Wizard ---
    if config.get("first_run", True):
        logger.info("First run detected, showing onboarding wizard...")
        wizard = OnboardingWizard()
        
        if wizard.exec() == OnboardingWizard.DialogCode.Accepted:
            # Récupérer la configuration du wizard
            wizard_config = wizard.get_configuration()
            config.update(wizard_config)
            
            # Sauvegarder avec protection
            protector.save_config(config)
            logger.info(f"Onboarding completed. Blocked apps: {config['blocked_apps']}")
        else:
            logger.warning("Onboarding cancelled by user")
            # Continuer quand même mais marquer first_run comme terminé
            config["first_run"] = False
            protector.save_config(config)
    
    # Initialize Components
    fetcher = ChallengeFetcher(local_path="assets/challenges.json")
    logger.info("Challenge fetcher initialized")
    
    # Bridge for thread-safe communication
    bridge = SignalBridge()
    
    # Blocker Setup
    all_blocked = config.get("blocked_apps", []) + config.get("custom_apps", [])
    blocker = ProcessBlocker(all_blocked)
    logger.info(f"Process blocker initialized with {len(all_blocked)} apps")
    
    # GUI Setup
    window = OverlayWindow(fetcher, initial_settings=config)
    logger.info("GUI initialized")
    
    # Wiring
    def on_block_detected():
        """Callback quand une app est bloquée"""
        # Afficher l'overlay
        bridge.request_overlay.emit()
        
        # Notification
        # Note: On ne sait pas quelle app a été bloquée ici, 
        # mais on pourrait l'ajouter au callback si besoin
        logger.info("App blocked, showing challenge overlay")
    
    def on_settings_changed(new_settings):
        """Callback quand les paramètres changent"""
        logger.info("Settings changed, updating components...")
        
        # Sauvegarder avec protection
        protector.save_config(new_settings)
        
        # Créer backup avant modification
        protector.create_backup()
        
        # Update Blocker
        all_apps = new_settings.get("blocked_apps", []) + new_settings.get("custom_apps", [])
        blocker.update_blocked_apps(all_apps)
        
        logger.info(f"Updated blocked apps: {all_apps}")
    
    def on_challenge_solved():
        """Callback quand un challenge est résolu"""
        logger.log_event("CHALLENGE_SOLVED", {
            "timestamp": str(notifier.stats.get("last_reset")),
            "total_solved": notifier.stats.get("challenges_solved", 0)
        })
        # Notification sera gérée dans main_gui.py si besoin
    
    # Connect signals
    bridge.request_overlay.connect(window.showFullScreen)
    window.unblock_signal.connect(blocker.unblock_all)
    window.settings_changed.connect(on_settings_changed)
    
    # Start Blocker
    blocker.on_block_callback = on_block_detected 
    blocker.start()
    logger.info("Process blocker started")
    
    # Notification de démarrage
    notifier.notify_startup()
    logger.info("CodeGate fully initialized and running")
    
    # Lancer l'application
    try:
        exit_code = app.exec()
        logger.info(f"Application exiting with code {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        logger.exception("Critical error in main loop")
        sys.exit(1)


if __name__ == "__main__":
    main()
