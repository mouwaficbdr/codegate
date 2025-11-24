import sys
import json
import psutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QTextEdit, QPushButton, QMessageBox, QDialog, 
                               QComboBox, QListWidget, QListWidgetItem, QTabWidget, QSplitter, 
                               QTextBrowser, QFormLayout, QLineEdit, QInputDialog, QScrollArea)
from PySide6.QtCore import Qt, Signal, Slot, QRegularExpression, QThread
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QIcon

from src.i18n_manager import I18nManager
from src.code_runner import CodeRunner

# Applications populaires par catégorie
COMMON_APPS = {
    "Navigateurs": [
        ("Firefox", "firefox"),
        ("Google Chrome", "chrome"),
        ("Chromium", "chromium-browser"),
        ("Brave", "brave-browser"),
        ("Opera", "opera"),
        ("Microsoft Edge", "microsoft-edge"),
    ],
    "Communication": [
        ("Discord", "discord"),
        ("Slack", "slack"),
        ("Telegram", "telegram-desktop"),
        ("Signal", "signal-desktop"),
        ("Thunderbird", "thunderbird"),
        ("Evolution", "evolution"),
    ],
    "Jeux & Divertissement": [
        ("Steam", "steam"),
        ("Spotify", "spotify"),
        ("VLC", "vlc"),
        ("Rhythmbox", "rhythmbox"),
        ("GIMP", "gimp"),
    ],
    "Développement": [
        ("VS Code", "code"),
        ("PyCharm", "pycharm"),
        ("IntelliJ IDEA", "idea"),
        ("Sublime Text", "sublime_text"),
        ("Atom", "atom"),
        ("Eclipse", "eclipse"),
    ],
}

# --- Syntax Highlighter (Multi-language) ---
class CodeHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None, language="python"):
        super().__init__(parent)
        self.language = language
        self.highlighting_rules = []
        self.setup_rules()

    def set_language(self, language):
        """Change le langage de coloration et raffraîchit l'affichage"""
        self.language = language
        self.setup_rules()
        self.rehighlight()

    def setup_rules(self):
        """Configure les règles de coloration selon le langage"""
        self.highlighting_rules = []

        # Format pour les mots-clés
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))  # Blue
        keyword_format.setFontWeight(QFont.Bold)

        # Format pour les chaînes
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))  # Orange

        # Format pour les commentaires
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))  # Green

        # Format pour les nombres
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))  # Light green

        # Mots-clés spécifiques au langage
        if self.language == "python":
            keywords = [
                "def", "class", "if", "else", "elif", "while", "for", "in", "return", 
                "import", "from", "as", "pass", "try", "except", "finally", "with",
                "raise", "assert", "break", "continue", "yield", "lambda", "and", 
                "or", "not", "is", "None", "True", "False", "self", "print", "len",
                "range", "str", "int", "float", "list", "dict", "set", "tuple"
            ]
            # Commentaires Python (#)
            self.highlighting_rules.append((QRegularExpression("#[^\\n]*"), comment_format))
            
        elif self.language == "javascript":
            keywords = [
                "function", "const", "let", "var", "if", "else", "for", "while", "do",
                "switch", "case", "break", "continue", "return", "try", "catch", 
                "finally", "throw", "new", "this", "typeof", "instanceof", "delete",
                "in", "of", "class", "extends", "super", "static", "async", "await",
                "null", "undefined", "true", "false", "console", "log", "push", "pop"
            ]
            # Commentaires JavaScript (//)
            self.highlighting_rules.append((QRegularExpression("//[^\\n]*"), comment_format))
            # Commentaires multi-lignes (/* */)
            self.highlighting_rules.append((QRegularExpression("/\\*.*\\*/"), comment_format))
            
        elif self.language == "php":
            keywords = [
                "function", "if", "else", "elseif", "while", "for", "foreach", "do",
                "switch", "case", "break", "continue", "return", "try", "catch",
                "finally", "throw", "new", "class", "extends", "public", "private",
                "protected", "static", "const", "var", "echo", "print", "array",
                "true", "false", "null", "as", "and", "or", "require", "include",
                "isset", "empty", "unset", "die", "exit", "$this", "self", "parent"
            ]
            # Commentaires PHP (// et #)
            self.highlighting_rules.append((QRegularExpression("//[^\\n]*"), comment_format))
            self.highlighting_rules.append((QRegularExpression("#[^\\n]*"), comment_format))
            # Commentaires multi-lignes (/* */)
            self.highlighting_rules.append((QRegularExpression("/\\*.*\\*/"), comment_format))

        # Ajouter les mots-clés
        for word in keywords:
            # Échapper les caractères spéciaux comme $
            escaped_word = word.replace("$", "\\$")
            pattern = QRegularExpression(f"\\b{escaped_word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        # Chaînes de caractères (doubles et simples guillemets)
        self.highlighting_rules.append((QRegularExpression('"[^"\\\\]*(\\\\.[^"\\\\]*)*"'), string_format))
        self.highlighting_rules.append((QRegularExpression("'[^'\\\\]*(\\\\.[^'\\\\]*)*'"), string_format))

        # Nombres
        self.highlighting_rules.append((QRegularExpression("\\b[0-9]+\\.?[0-9]*\\b"), number_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


# --- Settings Dialog (Modernized) ---
class SettingsDialog(QDialog):
    def __init__(self, i18n, current_settings, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.settings = current_settings.copy() # Travailler sur une copie
        self.setWindowTitle(self.i18n.get("settings"))
        self.resize(800, 600)
        self.init_ui()

    def init_ui(self):
        # Style global de la fenêtre
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: #d4d4d4; font-family: 'Segoe UI', 'Roboto', sans-serif; }
            QLabel { font-size: 14px; color: #d4d4d4; }
            QLabel#Title { font-size: 24px; font-weight: bold; color: #ffffff; margin-bottom: 20px; }
            QLabel#SectionTitle { font-size: 18px; font-weight: bold; color: #4A9EFF; margin-top: 10px; margin-bottom: 10px; }
            QPushButton { background-color: #0E639C; border: none; color: white; padding: 8px 16px; border-radius: 4px; font-size: 13px; }
            QPushButton:hover { background-color: #1177BB; }
            QPushButton#Secondary { background-color: #3C3C3C; }
            QPushButton#Secondary:hover { background-color: #4C4C4C; }
            QPushButton#Danger { background-color: #8B0000; }
            QPushButton#Danger:hover { background-color: #A00000; }
            QLineEdit { background-color: #3C3C3C; border: 1px solid #555; color: white; padding: 8px; border-radius: 4px; }
            QLineEdit:focus { border: 1px solid #0E639C; }
            QComboBox { background-color: #3C3C3C; border: 1px solid #555; color: white; padding: 5px; border-radius: 4px; min-width: 100px; }
            QComboBox::drop-down { border: none; }
            QListWidget { background-color: #252526; border: 1px solid #333; border-radius: 4px; outline: none; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #2d2d2d; }
            QListWidget::item:selected { background-color: #094771; }
            QListWidget::item:hover { background-color: #2a2d2e; }
            QScrollArea { border: none; background-color: transparent; }
            QScrollBar:vertical { border: none; background: #1e1e1e; width: 10px; margin: 0px; }
            QScrollBar::handle:vertical { background: #424242; min-height: 20px; border-radius: 5px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Sidebar ---
        sidebar = QWidget()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("background-color: #252526; border-right: 1px solid #333;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Titre Sidebar
        app_title = QLabel("🛡️ CodeGate")
        app_title.setAlignment(Qt.AlignCenter)
        app_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #4A9EFF; padding: 20px;")
        sidebar_layout.addWidget(app_title)

        # Menu Items
        self.menu_list = QListWidget()
        self.menu_list.setStyleSheet("""
            QListWidget { background-color: transparent; border: none; }
            QListWidget::item { padding: 15px 20px; font-size: 14px; border-left: 3px solid transparent; }
            QListWidget::item:selected { background-color: #1e1e1e; border-left: 3px solid #4A9EFF; color: white; }
            QListWidget::item:hover { background-color: #2a2d2e; }
        """)
        
        items = [
            ("Général", "⚙"),
            ("Applications Bloquées", "🚫"),
            ("À propos", "ℹ")
        ]
        
        for text, icon in items:
            item = QListWidgetItem(f"{icon}  {text}")
            self.menu_list.addItem(item)
            
        self.menu_list.setCurrentRow(0)
        self.menu_list.currentRowChanged.connect(self.change_page)
        sidebar_layout.addWidget(self.menu_list)
        
        # Version info at bottom
        version_label = QLabel("v1.0.0")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet("color: #666; padding: 10px;")
        sidebar_layout.addWidget(version_label)

        main_layout.addWidget(sidebar)

        # --- Content Area ---
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(30, 30, 30, 30)

        # Stacked Widget pour les pages
        self.pages = QTabWidget() # On utilise QTabWidget mais on cache les tabs pour faire un stacked widget custom
        self.pages.tabBar().hide()
        self.pages.setStyleSheet("QTabWidget::pane { border: none; }")
        
        # Page 1: Général
        self.pages.addTab(self.create_general_page(), "General")
        
        # Page 2: Apps Bloquées
        self.pages.addTab(self.create_apps_page(), "Blocked Apps")
        
        # Page 3: À propos
        self.pages.addTab(self.create_about_page(), "About")

        content_layout.addWidget(self.pages)

        # Footer Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton(self.i18n.get("cancel"))
        cancel_btn.setObjectName("Secondary")
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Enregistrer")
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(save_btn)
        
        content_layout.addLayout(buttons_layout)
        main_layout.addWidget(content_area)

    def change_page(self, index):
        self.pages.setCurrentIndex(index)

    def create_general_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignTop)
        
        title = QLabel("Paramètres Généraux")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        # Langue
        layout.addWidget(QLabel("Langue de l'interface", objectName="SectionTitle"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["en", "fr"])
        self.lang_combo.setCurrentText(self.settings.get("language", "en"))
        layout.addWidget(self.lang_combo)
        layout.addWidget(QLabel("La langue sera mise à jour au prochain démarrage de l'interface.", styleSheet="color: #888; font-size: 12px;"))
        
        layout.addSpacing(20)
        
        # Difficulté
        layout.addWidget(QLabel("Difficulté des Challenges", objectName="SectionTitle"))
        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Easy", "Medium", "Hard", "Mixed"])
        self.diff_combo.setCurrentText(self.settings.get("difficulty_mode", "Mixed"))
        layout.addWidget(self.diff_combo)
        
        desc_label = QLabel(
            "• Easy: Concepts de base\n"
            "• Medium: Algorithmes simples\n"
            "• Hard: Algorithmes complexes\n"
            "• Mixed: Mélange aléatoire (recommandé)"
        )
        desc_label.setStyleSheet("color: #888; margin-top: 5px;")
        layout.addWidget(desc_label)
        
        layout.addStretch()
        return page

    def create_apps_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        
        title = QLabel("Applications Bloquées")
        title.setObjectName("Title")
        layout.addWidget(title)
        
        # Header avec recherche et ajout
        header_layout = QHBoxLayout()
        
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("🔍 Rechercher une application...")
        self.search_field.textChanged.connect(self.filter_apps)
        header_layout.addWidget(self.search_field)
        
        add_btn = QPushButton("+ Ajouter")
        add_btn.setToolTip("Ajouter une application personnalisée par nom de processus")
        add_btn.clicked.connect(self.add_custom_app)
        header_layout.addWidget(add_btn)
        
        layout.addLayout(header_layout)
        
        # Liste des apps
        self.apps_list = QListWidget()
        layout.addWidget(self.apps_list)
        
        # Légende
        legend = QLabel("🟢 = En cours d'exécution  |  ✏️ = Personnalisé")
        legend.setStyleSheet("color: #888; font-size: 12px;")
        layout.addWidget(legend)
        
        # Initialiser les données
        self.current_blocked = set(self.settings.get("blocked_apps", []))
        self.custom_apps = set(self.settings.get("custom_apps", []))
        self.populate_apps_list()
        
        return page

    def create_about_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignCenter)
        
        title = QLabel("🛡️ CodeGate")
        title.setStyleSheet("font-size: 32px; font-weight: bold; color: #4A9EFF;")
        layout.addWidget(title)
        
        subtitle = QLabel("Productivité par le Code")
        subtitle.setStyleSheet("font-size: 16px; color: #d4d4d4; margin-bottom: 20px;")
        layout.addWidget(subtitle)
        
        info = QLabel(
            "Version 1.0.0\n\n"
            "Développé avec ❤️ pour vous aider à rester concentré.\n"
            "Chaque distraction est une opportunité d'apprendre."
        )
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        layout.addStretch()
        
        github_link = QLabel('<a href="#" style="color: #4A9EFF;">GitHub Repository</a>')
        github_link.setOpenExternalLinks(True)
        layout.addWidget(github_link)
        
        return page

    def populate_apps_list(self):
        """Peuple la liste des applications"""
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
            pass # Fallback si psutil échoue
        
        added_processes = set()
        
        # 1. Catégories prédéfinies
        for category, apps in COMMON_APPS.items():
            # Header
            cat_item = QListWidgetItem(f"{category}")
            cat_item.setFlags(Qt.NoItemFlags)
            cat_item.setBackground(QColor("#333"))
            cat_item.setForeground(QColor("#4A9EFF"))
            font = cat_item.font()
            font.setBold(True)
            cat_item.setFont(font)
            self.apps_list.addItem(cat_item)
            
            for display_name, process_name in apps:
                self._add_app_item(display_name, process_name, running_apps, added_processes)

        # 2. Apps personnalisées
        if self.custom_apps:
            custom_header = QListWidgetItem("Applications Personnalisées")
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

        # 3. Autres processus en cours (optionnel, peut-être trop bruyant, on met juste ceux bloqués non listés ailleurs)
        # Pour l'instant, on n'affiche pas TOUS les processus, seulement ceux déjà bloqués ou dans les listes.
        # Si l'utilisateur veut bloquer un autre process, il utilise "Ajouter".
        
        # Vérifier s'il y a des apps bloquées qui ne sont pas encore affichées (cas rare)
        remaining_blocked = self.current_blocked - added_processes
        if remaining_blocked:
            other_header = QListWidgetItem("Autres Bloquées")
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
        is_running = process_name in running_apps
        is_blocked = process_name in self.current_blocked
        
        text = f"  {display_name}"
        if is_custom: text += " ✏️"
        if is_running: text += " 🟢"
        
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, process_name)
        item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
        item.setCheckState(Qt.Checked if is_blocked else Qt.Unchecked)
        
        self.apps_list.addItem(item)
        added_processes.add(process_name)

    def filter_apps(self, search_text):
        search_text = search_text.lower()
        for i in range(self.apps_list.count()):
            item = self.apps_list.item(i)
            if item.flags() & Qt.ItemIsUserCheckable:
                text = item.text().lower()
                process = item.data(Qt.UserRole).lower()
                item.setHidden(search_text not in text and search_text not in process)
            else:
                # Headers : on pourrait être plus malin et les cacher si tous leurs enfants sont cachés
                pass

    def add_custom_app(self):
        process_name, ok = QInputDialog.getText(
            self, "Ajouter une application", 
            "Nom du processus (ex: notepad.exe, vlc):"
        )
        if ok and process_name:
            process_name = process_name.strip()
            if process_name:
                self.custom_apps.add(process_name)
                self.current_blocked.add(process_name) # On le bloque par défaut quand on l'ajoute
                self.populate_apps_list()
                # Scroll to bottom to see it (ou vers la section custom)
                self.apps_list.scrollToBottom()

    def get_settings(self):
        # Récupérer l'état des cases à cocher
        blocked = []
        for i in range(self.apps_list.count()):
            item = self.apps_list.item(i)
            if item.flags() & Qt.ItemIsUserCheckable and item.checkState() == Qt.Checked:
                blocked.append(item.data(Qt.UserRole))
        
        return {
            "language": self.lang_combo.currentText(),
            "difficulty_mode": self.diff_combo.currentText(),
            "blocked_apps": blocked,
            "custom_apps": list(self.custom_apps)
        }

# --- Worker Thread for Tests ---
class TestRunnerThread(QThread):
    finished = Signal(dict)

    def __init__(self, code_runner, user_code, func_name, tests, language, types):
        super().__init__()
        self.code_runner = code_runner
        self.user_code = user_code
        self.func_name = func_name
        self.tests = tests
        self.language = language
        self.types = types

    def run(self):
        result = self.code_runner.run_tests(
            self.user_code, self.func_name, self.tests, self.language, self.types
        )
        self.finished.emit(result)

# --- Main Overlay ---
class OverlayWindow(QMainWindow):
    unblock_signal = Signal()
    settings_changed = Signal(dict)

    def __init__(self, challenge_fetcher, initial_settings=None):
        super().__init__()
        self.challenge_fetcher = challenge_fetcher
        self.code_runner = CodeRunner()
        self.i18n = I18nManager()
        self.settings = initial_settings if initial_settings else {"language": "en", "difficulty_mode": "Mixed", "blocked_apps": []}
        
        self.i18n.set_language(self.settings.get("language", "en"))

        self.current_challenge = None
        self.init_ui()
        self.load_new_challenge()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

        # Main Container
        main_widget = QWidget()
        main_widget.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: #d4d4d4; font-family: 'Consolas', 'Monospace'; }
            QSplitter::handle { background-color: #333; }
            QTextEdit { background-color: #1e1e1e; border: none; font-size: 14px; }
            QTextBrowser { background-color: #1e1e1e; border: none; font-size: 14px; color: #d4d4d4; }
            QLabel { font-size: 14px; }
            QPushButton { background-color: #0E639C; border: none; color: white; padding: 8px 16px; border-radius: 2px; }
            QPushButton:hover { background-color: #1177BB; }
            QPushButton:disabled { background-color: #333; color: #888; }
            QPushButton#Secondary { background-color: #3C3C3C; }
            QPushButton#Secondary:hover { background-color: #4C4C4C; }
            QComboBox { background-color: #3C3C3C; border: none; padding: 5px; }
        """)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Header Bar ---
        header = QHBoxLayout()
        header.setContentsMargins(10, 10, 10, 10)
        
        # Titre CodeGate stylisé
        title_label = QLabel("🛡️ CodeGate")
        title_font = title_label.font()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #4A9EFF; padding: 5px;")
        header.addWidget(title_label)
        
        header.addStretch()
        
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["python", "javascript", "php"])
        self.lang_selector.currentTextChanged.connect(self.on_language_changed)
        header.addWidget(self.lang_selector)

        self.settings_btn = QPushButton()
        # Créer l'icône d'engrenage
        import os
        icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "settings_icon.svg")
        if os.path.exists(icon_path):
            self.settings_btn.setIcon(QIcon(icon_path))
        else:
            self.settings_btn.setText("⚙")  # Fallback si l'icône n'existe pas
        self.settings_btn.setFixedSize(32, 32)
        self.settings_btn.setToolTip("Paramètres")
        self.settings_btn.clicked.connect(self.open_settings)
        header.addWidget(self.settings_btn)
        
        main_layout.addLayout(header)

        # --- Splitter Content ---
        splitter = QSplitter(Qt.Horizontal)
        
        # Left Panel: Description (Rich Text)
        desc_widget = QWidget()
        desc_layout = QVBoxLayout(desc_widget)
        desc_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title + Badge
        title_layout = QHBoxLayout()
        self.title_label = QLabel("Challenge Title")
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #fff;")
        title_layout.addWidget(self.title_label)
        
        self.diff_badge = QLabel("Easy")
        self.diff_badge.setAlignment(Qt.AlignCenter)
        self.diff_badge.setFixedSize(60, 24)
        title_layout.addWidget(self.diff_badge)
        
        title_layout.addStretch()
        desc_layout.addLayout(title_layout)
        
        # Rich Text Description
        self.desc_browser = QTextBrowser()
        self.desc_browser.setOpenExternalLinks(True)
        desc_layout.addWidget(self.desc_browser)
        
        splitter.addWidget(desc_widget)

        # Right Panel: Editor + Console (Vertical Split)
        right_splitter = QSplitter(Qt.Vertical)
        
        # Editor Area
        editor_widget = QWidget()
        editor_layout = QVBoxLayout(editor_widget)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        editor_label = QLabel("Solution:")
        editor_label.setStyleSheet("background-color: #252526; padding: 5px; font-weight: bold;")
        editor_layout.addWidget(editor_label)
        
        self.code_editor = QTextEdit()
        self.highlighter = CodeHighlighter(self.code_editor.document(), language="python")
        editor_layout.addWidget(self.code_editor)
        
        right_splitter.addWidget(editor_widget)

        # Console Area
        console_widget = QWidget()
        console_layout = QVBoxLayout(console_widget)
        console_layout.setContentsMargins(0, 0, 0, 0)
        
        console_header = QHBoxLayout()
        console_label = QLabel("Test Output:")
        console_label.setStyleSheet("background-color: #252526; padding: 5px; font-weight: bold;")
        console_header.addWidget(console_label)
        console_header.addStretch()
        console_layout.addLayout(console_header)
        
        self.console_output = QTextBrowser() # Changed to Browser for HTML
        self.console_output.setOpenExternalLinks(False)
        self.console_output.setStyleSheet("background-color: #1e1e1e; font-family: monospace;")
        console_layout.addWidget(self.console_output)
        
        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(10, 10, 10, 10)
        
        self.run_btn = QPushButton("Run Sample Tests")
        self.run_btn.setObjectName("Secondary")
        self.run_btn.clicked.connect(self.run_sample_tests)
        btn_layout.addWidget(self.run_btn)
        
        btn_layout.addStretch()
        
        self.submit_btn = QPushButton("Attempt")
        self.submit_btn.clicked.connect(self.attempt_solution)
        btn_layout.addWidget(self.submit_btn)
        
        console_layout.addLayout(btn_layout)
        
        right_splitter.addWidget(console_widget)
        
        # Set Splitter Ratios
        splitter.addWidget(right_splitter)
        splitter.setStretchFactor(0, 1) 
        splitter.setStretchFactor(1, 2) 
        right_splitter.setStretchFactor(0, 2) 
        right_splitter.setStretchFactor(1, 1) 

        main_layout.addWidget(splitter)
        self.setCentralWidget(main_widget)

    # ... (Settings & Lang Logic) ...
    def open_settings(self):
        dialog = SettingsDialog(self.i18n, self.settings, self)
        if dialog.exec():
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            self.i18n.set_language(self.settings["language"])
            self.refresh_ui_text()
            self.settings_changed.emit(self.settings)

    def refresh_ui_text(self):
        pass 
        # TODO: Implémenter le rafraîchissement des textes de l'UI si la langue change
        # Pour l'instant, seul le contenu dynamique change.

    def load_new_challenge(self):
        self.current_challenge = self.challenge_fetcher.get_random_challenge()
        if self.current_challenge:
            self.title_label.setText(self.current_challenge['title'])
            
            diff = self.current_challenge.get('difficulty', 'Easy')
            self.diff_badge.setText(diff)
            if diff == "Easy":
                self.diff_badge.setStyleSheet("background-color: #4CAF50; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;")
            elif diff == "Medium":
                self.diff_badge.setStyleSheet("background-color: #FF9800; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;")
            else:
                self.diff_badge.setStyleSheet("background-color: #F44336; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 12px;")

            desc = self.current_challenge.get('description', '')
            obj = self.current_challenge.get('objective', '')
            constraints = self.current_challenge.get('constraints', '')
            examples = self.current_challenge.get('examples', '')
            
            html = f"""
            <h3 style="color: #9CDCFE;">Description</h3>
            <p>{desc}</p>
            <h3 style="color: #9CDCFE;">Objective</h3>
            <p>{obj}</p>
            <h3 style="color: #9CDCFE;">Constraints</h3>
            {constraints}
            <h3 style="color: #9CDCFE;">Examples</h3>
            {examples}
            """
            self.desc_browser.setHtml(html)
            
            self.on_language_changed(self.lang_selector.currentText())
            self.console_output.clear()
        else:
            self.desc_browser.setText("No challenges loaded.")

    def on_language_changed(self, lang):
        if not self.current_challenge:
            return
        templates = self.current_challenge.get("templates", {})
        template = templates.get(lang, f"// No template for {lang}")
        self.code_editor.setText(template)
        
        # Changer la coloration syntaxique selon le langage
        self.highlighter.set_language(lang)

    @Slot()
    def run_sample_tests(self):
        self._start_test_execution(unlock_on_success=False)

    @Slot()
    def attempt_solution(self):
        self._start_test_execution(unlock_on_success=True)

    def _start_test_execution(self, unlock_on_success):
        if not self.current_challenge:
            return

        # UI State: Running
        self.run_btn.setEnabled(False)
        self.submit_btn.setEnabled(False)
        self.console_output.setHtml("<p style='color: #DCDCAA;'>Running tests...</p>")
        
        user_code = self.code_editor.toPlainText()
        func_name = self.current_challenge.get("function_name", "solution")
        tests = self.current_challenge.get("tests", [])
        lang = self.lang_selector.currentText()
        types = self.current_challenge.get("types", None)
        
        # Start Thread
        self.thread = TestRunnerThread(self.code_runner, user_code, func_name, tests, lang, types)
        self.thread.finished.connect(lambda result: self._on_tests_finished(result, unlock_on_success))
        self.thread.start()

    def _on_tests_finished(self, result, unlock_on_success):
        # UI State: Ready
        self.run_btn.setEnabled(True)
        self.submit_btn.setEnabled(True)
        
        success = result.get("success", False)
        error = result.get("error")
        results = result.get("results", [])
        
        html_output = ""
        
        if error:
            html_output += f"<h4 style='color: #F44336;'>Execution Error:</h4><pre style='color: #F44336;'>{error}</pre>"
        else:
            passed_count = sum(1 for r in results if r['passed'])
            total_count = len(results)
            
            color = "#4CAF50" if success else "#F44336"
            html_output += f"<h4 style='color: {color};'>Result: {passed_count}/{total_count} Passed</h4>"
            
            for i, r in enumerate(results):
                status_color = "#4CAF50" if r['passed'] else "#F44336"
                status_icon = "✔" if r['passed'] else "✘"
                
                html_output += f"<div style='margin-bottom: 10px; border-left: 3px solid {status_color}; padding-left: 10px;'>"
                html_output += f"<div style='color: {status_color}; font-weight: bold;'>Test {i+1}: {status_icon}</div>"
                html_output += f"<div>Input: <span style='color: #9CDCFE;'>{r['input']}</span></div>"
                
                if not r['passed']:
                     html_output += f"<div>Expected: <span style='color: #CE9178;'>{r['expected']}</span></div>"
                     html_output += f"<div>Actual: <span style='color: #F44336;'>{r['actual']}</span></div>"
                     if r.get('log'):
                         html_output += f"<pre style='color: #888; font-size: 12px;'>{r['log']}</pre>"
                html_output += "</div>"

        self.console_output.setHtml(html_output)

        if success and unlock_on_success:
             QMessageBox.information(self, "Success", "All tests passed! Unlocking...")
             self.unblock_signal.emit()
             self.close()

if __name__ == "__main__":
    from challenge_fetcher import ChallengeFetcher
    app = QApplication(sys.argv)
    fetcher = ChallengeFetcher(local_path="../assets/challenges.json")
    window = OverlayWindow(fetcher)
    window.show()
    sys.exit(app.exec())
