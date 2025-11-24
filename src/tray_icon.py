from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject
import os

class CodeGateTray(QSystemTrayIcon):
    request_settings = Signal()
    request_quit = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        # Charger l'icône
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "codegate_icon.svg")
        if os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
        else:
            # Fallback si l'icône n'est pas trouvée (ne devrait pas arriver si le fichier est créé)
            pass

        # Créer le menu contextuel
        menu = QMenu()
        
        # Style du menu (tentative de dark mode, dépend du système)
        menu.setStyleSheet("""
            QMenu {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #333;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
        """)

        # Action Paramètres
        settings_action = QAction("⚙ Paramètres", self)
        settings_action.triggered.connect(self.request_settings.emit)
        menu.addAction(settings_action)

        menu.addSeparator()

        # Action Quitter
        quit_action = QAction("❌ Quitter CodeGate", self)
        quit_action.triggered.connect(self.request_quit.emit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.setToolTip("CodeGate - Productivité & Focus")
