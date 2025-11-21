import sys
import json
import psutil
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QLabel, QTextEdit, QPushButton, QMessageBox, QDialog, 
                               QComboBox, QListWidget, QListWidgetItem, QTabWidget, QSplitter, QTextBrowser)
from PySide6.QtCore import Qt, Signal, Slot, QRegularExpression, QThread
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont

from src.i18n_manager import I18nManager
from src.code_runner import CodeRunner

# --- Syntax Highlighter (Same as before) ---
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6")) # Blue
        keyword_format.setFontWeight(QFont.Bold)
        keywords = ["def", "class", "if", "else", "elif", "while", "for", "return", "import", "from", "pass", "try", "except", "print"]
        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178")) # Orange
        self.highlighting_rules.append((QRegularExpression("\".*\""), string_format))
        self.highlighting_rules.append((QRegularExpression("'.*'"), string_format))
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955")) # Green
        self.highlighting_rules.append((QRegularExpression("#[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

# --- Settings Dialog (Same as before) ---
class SettingsDialog(QDialog):
    def __init__(self, i18n, current_settings, parent=None):
        super().__init__(parent)
        self.i18n = i18n
        self.settings = current_settings
        self.setWindowTitle(self.i18n.get("settings"))
        self.resize(500, 400)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        tabs = QTabWidget()

        # Tab 1: General
        general_tab = QWidget()
        form = QFormLayout(general_tab)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["en", "fr"])
        self.lang_combo.setCurrentText(self.settings.get("language", "en"))
        form.addRow(self.i18n.get("language"), self.lang_combo)

        self.diff_combo = QComboBox()
        self.diff_combo.addItems(["Easy", "Medium", "Hard", "Mixed"])
        self.diff_combo.setCurrentText(self.settings.get("difficulty_mode", "Mixed"))
        form.addRow(self.i18n.get("difficulty"), self.diff_combo)
        
        tabs.addTab(general_tab, "General")

        # Tab 2: Blocked Apps
        apps_tab = QWidget()
        apps_layout = QVBoxLayout(apps_tab)
        
        apps_layout.addWidget(QLabel("Select apps to block:"))
        
        self.apps_list = QListWidget()
        current_blocked = set(self.settings.get("blocked_apps", []))
        
        # Get running processes
        running_apps = set()
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name']
                if name:
                    running_apps.add(name)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        all_apps = sorted(list(running_apps.union(current_blocked)))
        
        for app_name in all_apps:
            item = QListWidgetItem(app_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if app_name in current_blocked:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.apps_list.addItem(item)
            
        apps_layout.addWidget(self.apps_list)
        tabs.addTab(apps_tab, "Blocked Apps")

        layout.addWidget(tabs)

        # Buttons
        btn_box = QHBoxLayout()
        save_btn = QPushButton(self.i18n.get("save"))
        save_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton(self.i18n.get("cancel"))
        cancel_btn.clicked.connect(self.reject)
        btn_box.addWidget(save_btn)
        btn_box.addWidget(cancel_btn)
        layout.addLayout(btn_box)

    def get_settings(self):
        blocked = []
        for i in range(self.apps_list.count()):
            item = self.apps_list.item(i)
            if item.checkState() == Qt.Checked:
                blocked.append(item.text())

        return {
            "language": self.lang_combo.currentText(),
            "difficulty_mode": self.diff_combo.currentText(),
            "blocked_apps": blocked
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
        header.addWidget(QLabel("CodeGate"))
        
        header.addStretch()
        
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["python", "javascript", "php"])
        self.lang_selector.currentTextChanged.connect(self.on_language_changed)
        header.addWidget(self.lang_selector)

        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedWidth(30)
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
        self.highlighter = PythonHighlighter(self.code_editor.document())
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
