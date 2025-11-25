from PySide6.QtWidgets import QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction
from PySide6.QtCore import Signal, QObject
import os
from src.i18n_manager import I18nManager

class CodeGateTray(QSystemTrayIcon):
    request_settings = Signal()
    request_quit = Signal()

    def __init__(self, parent=None, lang="en"):
        super().__init__(parent)
        self.i18n = I18nManager(lang)
        self.init_ui()

    def set_language(self, lang):
        """Mettre à jour la langue et recréer le menu"""
        self.i18n.set_language(lang)
        self.setToolTip(self.i18n.get("tray_tooltip"))
        # Re-créer le menu pour mettre à jour les textes
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
        # Style du menu (tentative de dark mode, dépend du système)
        menu.setStyleSheet("""
            QMenu {
                background-color: #18181b;
                color: #e4e4e7;
                border: 1px solid #3f3f46;
                font-family: 'Segoe UI', 'Roboto', sans-serif;
            }
            QMenu::item {
                padding: 8px 24px;
            }
            QMenu::item:selected {
                background-color: #3b82f6;
                color: white;
            }
            QMenu::separator {
                height: 1px;
                background: #3f3f46;
                margin: 4px 0px;
            }
        """)

        # Action Paramètres
        settings_action = QAction(self.i18n.get("settings"), self)
        settings_action.triggered.connect(self.request_settings.emit)
        menu.addAction(settings_action)

        menu.addSeparator()

        # Action Quitter
        quit_action = QAction(self.i18n.get("quit"), self)
        quit_action.triggered.connect(self.request_quit.emit)
        menu.addAction(quit_action)

        self.setContextMenu(menu)
        self.setToolTip(self.i18n.get("tray_tooltip"))
        
        # Connecter le signal activated pour gérer le clic gauche
        self.activated.connect(self.on_activated)

    def on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            # Sur un clic gauche (Trigger), on peut soit ouvrir le menu, soit ouvrir les paramètres
            # Ici, on choisit d'ouvrir le menu contextuel pour être cohérent
            self.contextMenu().popup(self.geometry().center())

