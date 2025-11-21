import sys
import json
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, Slot


from src.process_blocker import ProcessBlocker
from src.challenge_fetcher import ChallengeFetcher
from src.main_gui import OverlayWindow

class SignalBridge(QObject):
    request_overlay = Signal()

def main():
    app = QApplication(sys.argv)

    # Load Config
    config_path = "config.json"
    config = {}
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            config = json.load(f)
    else:
        # Default config creation
        config = {
            "blocked_apps": ["calculator", "gedit", "discord"],
            "language": "en",
            "difficulty_mode": "Mixed"
        }
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=4)

    # Initialize Components
    fetcher = ChallengeFetcher(local_path="assets/challenges.json")
    
    # Bridge for thread-safe communication
    bridge = SignalBridge()
    
    # Blocker Setup
    blocker = ProcessBlocker(config.get("blocked_apps", []))
    
    # GUI Setup
    window = OverlayWindow(fetcher, initial_settings=config)

    # Wiring
    def on_block_detected():
        bridge.request_overlay.emit()

    def on_settings_changed(new_settings):
        # Update Config File
        with open(config_path, 'w') as f:
            json.dump(new_settings, f, indent=4)
        
        # Update Blocker
        blocker.update_blocked_apps(new_settings.get("blocked_apps", []))
        print(f"Updated blocked apps: {new_settings.get('blocked_apps', [])}")

    bridge.request_overlay.connect(window.showFullScreen)
    window.unblock_signal.connect(blocker.unblock_all)
    window.settings_changed.connect(on_settings_changed)
    
    # Start Blocker
    blocker.on_block_callback = on_block_detected 
    blocker.start()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
