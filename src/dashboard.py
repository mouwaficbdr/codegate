#!/usr/bin/env python3
"""
Dashboard - Fenêtre principale de gestion de CodeGate
Remplace SettingsDialog par une fenêtre persistante
"""

import psutil
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QListWidget, QListWidgetItem, QTabWidget,
                               QPushButton, QComboBox, QLineEdit, QInputDialog)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QCloseEvent

from src.i18n_manager import I18nManager

# Applications populaires par catégorie
COMMON_APPS = {
    "cat_browsers": [
        ("Firefox", "firefox"),
        ("Google Chrome", "chrome"),
        ("Chromium", "chromium-browser"),
        ("Brave", "brave-browser"),
        ("Opera", "opera"),
        ("Microsoft Edge", "microsoft-edge"),
    ],
    "cat_communication": [
        ("Discord", "discord"),
        ("Slack", "slack"),
        ("Telegram", "telegram-desktop"),
        ("Signal", "signal-desktop"),
        ("Thunderbird", "thunderbird"),
        ("Evolution", "evolution"),
    ],
    "cat_games": [
        ("Steam", "steam"),
        ("Spotify", "spotify"),
        ("VLC", "vlc"),
        ("Rhythmbox", "rhythmbox"),
        ("GIMP", "gimp"),
    ],
    "cat_dev": [
        ("VS Code", "code"),
        ("PyCharm", "pycharm"),
        ("IntelliJ IDEA", "idea"),
        ("Sublime Text", "sublime_text"),
        ("Atom", "atom"),
        ("Eclipse", "eclipse"),
    ],
}


class DashboardWindow(QMainWindow):
    """Fenêtre Dashboard principale de CodeGate"""
    
    settings_changed = Signal(dict)
    
    def __init__(self, i18n, current_settings, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.settings = current_settings.copy()
        self.first_run_mode = False
        self.force_setup = False
        
        self.setWindowTitle("CodeGate Dashboard")
        self.resize(900, 650)
        self.init_ui()
    
    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Style global
        self.setStyleSheet("""
            QMainWindow, QWidget { 
                background-color: #18181b; 
                color: #e4e4e7; 
                font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif; 
            }
            
            /* Labels */
            QLabel { 
                font-size: 14px; 
                color: #e4e4e7; 
            }
            QLabel#Title { 
                font-size: 24px; 
                font-weight: 700; 
                color: #ffffff; 
                margin-bottom: 24px; 
            }
            QLabel#SectionTitle { 
                font-size: 16px; 
                font-weight: 600; 
                color: #3b82f6; 
                margin-top: 16px; 
                margin-bottom: 8px; 
            }
            
            /* Buttons */
            QPushButton { 
                background-color: #3b82f6; 
                border: none; 
                color: white; 
                padding: 8px 16px; 
                border-radius: 6px; 
                font-size: 13px; 
                font-weight: 600;
            }
            QPushButton:hover { 
                background-color: #2563eb; 
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #27272a;
                color: #71717a;
                border: 1px solid #3f3f46;
            }
            
            /* Secondary Button */
            QPushButton#Secondary { 
                background-color: #27272a; 
                border: 1px solid #3f3f46;
                color: #e4e4e7;
            }
            QPushButton#Secondary:hover { 
                background-color: #3f3f46; 
                border-color: #52525b;
            }
            
            /* Inputs */
            QLineEdit { 
                background-color: #27272a; 
                border: 1px solid #3f3f46; 
                color: #e4e4e7; 
                padding: 8px; 
                border-radius: 6px; 
            }
            QLineEdit:focus { 
                border: 1px solid #3b82f6; 
            }
            
            /* Combo Box */
            QComboBox { 
                background-color: #27272a; 
                border: 1px solid #3f3f46; 
                color: #e4e4e7; 
                padding: 6px; 
                border-radius: 6px; 
                min-width: 100px; 
            }
            QComboBox::drop-down { 
                border: none; 
            }
            
            /* List Widget (Sidebar) */
            QListWidget { 
                background-color: #18181b; 
                border: none;
                outline: none; 
            }
            QListWidget::item { 
                padding: 12px 16px; 
                border-left: 3px solid transparent;
                color: #a1a1aa;
            }
            QListWidget::item:selected { 
                background-color: #27272a; 
                border-left: 3px solid #3b82f6; 
                color: #ffffff; 
            }
            QListWidget::item:hover { 
                background-color: #27272a; 
                color: #e4e4e7;
            }
            
            /* Scrollbars */
            QScrollBar:vertical { border: none; background: #18181b; width: 8px; margin: 0px; }
            QScrollBar::handle:vertical { background: #3f3f46; min-height: 20px; border-radius: 4px; }
            QScrollBar::handle:vertical:hover { background: #52525b; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Sidebar ---
        sidebar = self._create_sidebar()
        main_layout.addWidget(sidebar)
        
        # --- Content Area ---
        content_area = self._create_content_area()
        main_layout.addWidget(content_area)
    
    def _create_sidebar(self):
        """Créer la barre latérale de navigation"""
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #252526; border-right: 1px solid #333;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Titre
        app_title = QLabel("🛡️ CodeGate")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A9EFF; padding: 20px;")
        sidebar_layout.addWidget(app_title)
        
        # Menu
        self.menu_list = QListWidget()
        self.menu_list.setStyleSheet("""
            QListWidget { background-color: transparent; border: none; }
            QListWidget::item { padding: 15px 20px; font-size: 14px; border-left: 3px solid transparent; }
            QListWidget::item:selected { background-color: #1e1e1e; border-left: 3px solid #4A9EFF; color: white; }
            QListWidget::item:hover { background-color: #2a2d2e; }
        """)
        
        items = [
            (self.i18n.get("general"), "⚙"),
            (self.i18n.get("blocked_apps"), "🚫"),
            (self.i18n.get("about"), "ℹ")
        ]
        
        for text, icon in items:
            item = QListWidgetItem(f"{icon}  {text}")
            self.menu_list.addItem(item)
        
        self.menu_list.setCurrentRow(0)
        self.menu_list.currentRowChanged.connect(self._change_page)
        sidebar_layout.addWidget(self.menu_list)
        
        # Version
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #666; padding: 10px;")
        sidebar_layout.addWidget(version_label)
        
        return sidebar
    
    def _create_content_area(self):
        """Créer la zone de contenu"""
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)
        
        # Pages
        self.pages = QTabWidget()
        self.pages.tabBar().hide()
        self.pages.setStyleSheet("QTabWidget::pane { border: none; }")
        
        self.pages.addTab(self._create_general_page(), "General")
        self.pages.addTab(self._create_apps_page(), "Blocked Apps")
        self.pages.addTab(self._create_about_page(), "About")
        
        content_layout.addWidget(self.pages)
        
        # Footer avec boutons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.close_btn = QPushButton(self.i18n.get("cancel"))  # Réutiliser "cancel" au lieu de "close"
        self.close_btn.setObjectName("Secondary")
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(self.close_btn)
        
        self.save_btn = QPushButton(self.i18n.get("save"))
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._save_and_close)
        buttons_layout.addWidget(self.save_btn)
        
        content_layout.addLayout(buttons_layout)
        
        return content_area
    
    def _change_page(self, index):
        """Changer de page"""
        self.pages.setCurrentIndex(index)
    
    def _create_general_page(self):
        """Créer la page Général"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        title = QLabel(self.i18n.get("settings_title"))
        title.setObjectName("Title")
        layout.addWidget(title)
        
        # Langue
        layout.addWidget(QLabel(self.i18n.get("language"), objectName="SectionTitle"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["en", "fr"])
        self.lang_combo.setCurrentText(self.settings.get("language", "en"))
        layout.addWidget(self.lang_combo)
        layout.addWidget(QLabel(self.i18n.get("language_hint"), styleSheet="color: #888; font-size: 12px;"))
        
        layout.addSpacing(20)
        
        # Difficulté
        layout.addWidget(QLabel(self.i18n.get("difficulty"), objectName="SectionTitle"))
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Easy", "Medium", "Hard", "Mixed"])
        self.diff_combo.setCurrentText(self.settings.get("difficulty_mode", "Mixed"))
        layout.addWidget(self.diff_combo)
        
        desc_label = QLabel(
            f"{self.i18n.get('diff_easy_desc')}\\n"
            f"{self.i18n.get('diff_medium_desc')}\\n"
            f"{self.i18n.get('diff_hard_desc')}\\n"
            f"{self.i18n.get('diff_mixed_desc')}"
        )
        desc_label.setStyleSheet("color: #888; margin-top: 5px;")
        layout.addWidget(desc_label)
        
        layout.addStretch()
        return page
    
    def _create_apps_page(self):
        """Créer la page Applications Bloquées"""
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel(self.i18n.get("blocked_apps"))
        title.setObjectName("Title")
        layout.addWidget(title)
        
        # Header avec recherche et ajout
        header_layout = QHBoxLayout()
        
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText(self.i18n.get("search_placeholder"))
        self.search_field.textChanged.connect(self._filter_apps)
        header_layout.addWidget(self.search_field)
        
        add_btn = QPushButton(self.i18n.get("add_btn"))
        add_btn.setToolTip(self.i18n.get("add_tooltip"))
        add_btn.clicked.connect(self._add_custom_app)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Liste des apps
        self.apps_list = QListWidget()
        self.apps_list.itemChanged.connect(self._on_app_selection_changed)
        layout.addWidget(self.apps_list)
        
        # Légende
        legend = QLabel(self.i18n.get("legend"))
        legend.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(legend)
        
        # Initialiser les données
        self.current_blocked = set(self.settings.get("blocked_apps", []))
        self.custom_apps = set(self.settings.get("custom_apps", []))
        self._populate_apps_list()
        
        return page
    
    def _create_about_page(self):
        """Créer la page À propos"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("🛡️ CodeGate")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #4A9EFF;")
        layout.addWidget(title)
        
        subtitle = QLabel(self.i18n.get("about_subtitle"))
        subtitle.setStyleSheet("font-size: 16px; color: #d4d4d4; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        info = QLabel(self.i18n.get("about_desc"))
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        layout.addStretch()
        
        github_link = QLabel('<a href="#" style="color: #4A9EFF;">GitHub Repository</a>')
        github_link.setOpenExternalLinks(True)
        layout.addWidget(github_link)
        
        return page
    
    def _populate_apps_list(self):
        """Peupler la liste des applications"""
        self.apps_list.clear()
        
        running_apps = set()
        try:
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name']:
                        running_apps.add(proc.info['name'])
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
        except Exception:
            pass
        
        added_processes = set()
        
        # Catégories prédéfinies
        for category_key, apps in COMMON_APPS.items():
            cat_item = QListWidgetItem(self.i18n.get(category_key))
            cat_item.setFlags(Qt.NoItemFlags)
            cat_item.setBackground(QColor("#333"))
            cat_item.setForeground(QColor("#4A9EFF"))
            font = cat_item.font()
            font.setBold(True)
            cat_item.setFont(font)
            self.apps_list.addItem(cat_item)
            
            for display_name, process_name in apps:
                self._add_app_item(display_name, process_name, running_apps, added_processes)
        
        # Apps personnalisées
        if self.custom_apps:
            custom_header = QListWidgetItem(self.i18n.get("custom_apps"))
            custom_header.setFlags(Qt.NoItemFlags)
            custom_header.setBackground(QColor("#333"))
            custom_header.setForeground(QColor("#4A9EFF"))
            font = custom_header.font()
            font.setBold(True)
            custom_header.setFont(font)
            self.apps_list.addItem(custom_header)
            
            for process_name in sorted(self.custom_apps):
                if process_name not in added_processes:
                    self._add_app_item(process_name, process_name, running_apps, added_processes, is_custom=True)
        
        # Autres apps bloquées
        remaining_blocked = self.current_blocked - added_processes
        if remaining_blocked:
            other_header = QListWidgetItem(self.i18n.get("other_blocked"))
            other_header.setFlags(Qt.NoItemFlags)
            other_header.setBackground(QColor("#333"))
            other_header.setForeground(QColor("#4A9EFF"))
            font = other_header.font()
            font.setBold(True)
            other_header.setFont(font)
            self.apps_list.addItem(other_header)
            
            for process_name in remaining_blocked:
                self._add_app_item(process_name, process_name, running_apps, added_processes)
    
    def _add_app_item(self, display_name, process_name, running_apps, added_processes, is_custom=False):
        """Ajouter un item d'application à la liste"""
        is_running = process_name in running_apps
        is_blocked = process_name in self.current_blocked
        
        text = f"  {display_name}"
        if is_custom:
            text += " ✏️"
        if is_running:
            text += " 🟢"
        
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, process_name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if is_blocked else Qt.Unchecked)
        
        self.apps_list.addItem(item)
        added_processes.add(process_name)
    
    def _filter_apps(self, search_text):
        """Filtrer les applications"""
        search_text = search_text.lower()
        for i in range(self.apps_list.count()):
            item = self.apps_list.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                text = item.text().lower()
                process = item.data(Qt.UserRole).lower()
                item.setHidden(search_text not in text and search_text not in process)
    
    def _add_custom_app(self):
        """Ajouter une application personnalisée"""
        process_name, ok = QInputDialog.getText(
            self, self.i18n.get("add_custom_title"), 
            self.i18n.get("add_custom_msg")
        )
        if ok and process_name:
            process_name = process_name.strip()
            if process_name:
                self.custom_apps.add(process_name)
                self.current_blocked.add(process_name)
                self._populate_apps_list()
                self.apps_list.scrollToBottom()
    
    def _on_app_selection_changed(self):
        """Callback quand une app est cochée/décochée"""
        if self.force_setup:
            # Vérifier si au moins une app est bloquée
            has_blocked = any(
                self.apps_list.item(i).checkState() == Qt.Checked
                for i in range(self.apps_list.count())
                if self.apps_list.item(i).flags() & Qt.ItemIsUserCheckable
            )
            self.save_btn.setEnabled(has_blocked)
            self.close_btn.setEnabled(has_blocked)
    
    def _save_and_close(self):
        """Sauvegarder et fermer"""
        # Récupérer les apps bloquées
        blocked = []
        for i in range(self.apps_list.count()):
            item = self.apps_list.item(i)
            if item.flags() & Qt.ItemIsUserCheckable and item.checkState() == Qt.Checked:
                blocked.append(item.data(Qt.UserRole))
        
        # Mettre à jour les settings
        self.settings["language"] = self.lang_combo.currentText()
        self.settings["difficulty_mode"] = self.diff_combo.currentText()
        self.settings["blocked_apps"] = blocked
        self.settings["custom_apps"] = list(self.custom_apps)
        
        # Émettre le signal
        self.settings_changed.emit(self.settings)
        
        # Fermer la fenêtre
        self.close()
    
    def show_with_tutorial(self):
        """Afficher en mode First Run avec tutoriel"""
        self.first_run_mode = True
        self.show()
        # TODO: Afficher un overlay explicatif
    
    def force_initial_setup(self):
        """Forcer l'utilisateur à configurer au moins une app"""
        self.force_setup = True
        self.save_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        
        # Aller directement à la page Apps
        self.menu_list.setCurrentRow(1)
        self._change_page(1)
    
    def closeEvent(self, event: QCloseEvent):
        """Gérer la fermeture de la fenêtre"""
        if self.force_setup:
            # Vérifier si au moins une app est bloquée
            has_blocked = any(
                self.apps_list.item(i).checkState() == Qt.Checked
                for i in range(self.apps_list.count())
                if self.apps_list.item(i).flags() & Qt.ItemIsUserCheckable
            )
            if not has_blocked:
                event.ignore()
                return
        
        # Minimiser vers le tray au lieu de quitter
        event.ignore()
        self.hide()
    
    def get_settings(self):
        """Obtenir les paramètres actuels"""
        return self.settings.copy()
