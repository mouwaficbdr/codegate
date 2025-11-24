#!/usr/bin/env python3
"""
Onboarding - Welcome screen et configuration initiale
Interface guidée pour le premier lancement de CodeGate
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWizard, QWizardPage, QListWidget, QListWidgetItem, QTextEdit, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
import psutil
import os
from src.i18n_manager import I18nManager


class WelcomePage(QWizardPage):
    """Page d'accueil du wizard"""
    
    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.setTitle(self.i18n.get("welcome_title"))
        
        layout = QVBoxLayout()
        
        # Message de bienvenue
        welcome_text = QLabel(
            f"{self.i18n.get('welcome_subtitle')}"
            f"{self.i18n.get('welcome_intro')}"
            "<br>"
            f"{self.i18n.get('how_it_works')}"
            "<ol>"
            f"{self.i18n.get('step_1')}"
            f"{self.i18n.get('step_2')}"
            f"{self.i18n.get('step_3')}"
            f"{self.i18n.get('step_4')}"
            "</ol>"
            "<br>"
            f"{self.i18n.get('benefits_title')}"
            "<ul>"
            f"{self.i18n.get('benefit_1')}"
            f"{self.i18n.get('benefit_2')}"
            f"{self.i18n.get('benefit_3')}"
            "</ul>"
        )
        welcome_text.setWordWrap(True)
        welcome_text.setTextFormat(Qt.RichText)
        
        layout.addWidget(welcome_text)
        self.setLayout(layout)


class AppSelectionPage(QWizardPage):
    """Page de sélection des applications à bloquer"""
    
    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.setTitle(self.i18n.get("app_selection_title"))
        self.setSubTitle(self.i18n.get("app_selection_subtitle"))
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(self.i18n.get("app_selection_instr"))
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Liste d'applications populaires
        self.app_list = QListWidget()
        
        # Applications courantes
        common_apps = {
            "cat_browsers": ["firefox", "chrome", "chromium", "brave"],
            "cat_communication": ["discord", "slack", "telegram", "signal"],
            "cat_games": ["steam", "spotify"],
            "cat_social": ["whatsapp", "thunderbird"]
        }
        
        # Ajouter par catégorie
        for category_key, apps in common_apps.items():
            # Header de catégorie
            header_item = QListWidgetItem(f"📁 {self.i18n.get(category_key)}")
            header_item.setFlags(Qt.NoItemFlags)
            font = header_item.font()
            font.setBold(True)
            header_item.setFont(font)
            self.app_list.addItem(header_item)
            
            # Apps de la catégorie
            for app in apps:
                item = QListWidgetItem(f"  {app}")
                item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                item.setCheckState(Qt.Unchecked)
                item.setData(Qt.UserRole, app)  # Stocker le nom du process
                
                # Marquer si l'app tourne actuellement
                if self._is_process_running(app):
                    item.setText(f"  {app} 🟢")
                
                self.app_list.addItem(item)
        
        layout.addWidget(self.app_list)
        
        # Suggestion
        suggestion = QLabel(self.i18n.get("app_selection_tip"))
        suggestion.setWordWrap(True)
        layout.addWidget(suggestion)
        
        self.setLayout(layout)
    
    def _is_process_running(self, process_name):
        """Vérifier si un processus est en cours"""
        try:
            current_user = os.getlogin()
            for proc in psutil.process_iter(['name', 'username']):
                if proc.info['username'] == current_user and proc.info['name'] == process_name:
                    return True
        except:
            pass
        return False
    
    def get_selected_apps(self):
        """Obtenir la liste des apps sélectionnées"""
        selected = []
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            if item.checkState() == Qt.Checked:
                app_name = item.data(Qt.UserRole)
                if app_name:  # Ignorer les headers
                    selected.append(app_name)
        return selected


class DifficultyPage(QWizardPage):
    """Page de sélection de la difficulté"""
    
    def __init__(self, i18n):
        super().__init__()
        self.i18n = i18n
        self.setTitle(self.i18n.get("diff_title"))
        self.setSubTitle(self.i18n.get("diff_subtitle"))
        
        layout = QVBoxLayout()
        
        explanation = QLabel(self.i18n.get("diff_expl"))
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        
        # Options de difficulté
        self.easy_cb = QCheckBox(self.i18n.get("diff_easy"))
        self.medium_cb = QCheckBox(self.i18n.get("diff_medium"))
        self.hard_cb = QCheckBox(self.i18n.get("diff_hard"))
        self.mixed_cb = QCheckBox(self.i18n.get("diff_mixed"))
        
        self.mixed_cb.setChecked(True)  # Par défaut
        
        layout.addWidget(self.easy_cb)
        layout.addWidget(self.medium_cb)
        layout.addWidget(self.hard_cb)
        layout.addWidget(self.mixed_cb)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def get_difficulty(self):
        """Obtenir la difficulté sélectionnée"""
        if self.easy_cb.isChecked():
            return "Easy"
        elif self.medium_cb.isChecked():
            return "Medium"
        elif self.hard_cb.isChecked():
            return "Hard"
        else:
            return "Mixed"


class FinalPage(QWizardPage):
    """Page finale avec résumé"""
    
    def __init__(self, parent_wizard, i18n):
        super().__init__()
        self.wizard = parent_wizard
        self.i18n = i18n
        self.setTitle(self.i18n.get("final_title"))
        
        layout = QVBoxLayout()
        
        # Résumé
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setTextFormat(Qt.RichText)
        layout.addWidget(self.summary_label)
        
        # Auto-start info
        autostart_info = QLabel(
            f"{self.i18n.get('final_autostart')}"
            f"{self.i18n.get('final_settings')}"
        )
        autostart_info.setWordWrap(True)
        layout.addWidget(autostart_info)
        
        # Message final
        final_msg = QLabel(self.i18n.get("final_msg"))
        final_msg.setWordWrap(True)
        layout.addWidget(final_msg)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def initializePage(self):
        """Initialiser la page avec le résumé"""
        app_page = self.wizard.page(1)
        diff_page = self.wizard.page(2)
        
        selected_apps = app_page.get_selected_apps()
        difficulty = diff_page.get_difficulty()
        
        apps_text = "<br>".join([f"  • {app}" for app in selected_apps]) if selected_apps else f"  {self.i18n.get('no_apps')}"
        
        summary = (
            f"<p>{self.i18n.get('final_summary_apps', count=len(selected_apps))}<br>"
            f"{apps_text}</p>"
            f"<p>{self.i18n.get('final_summary_diff', diff=difficulty)}</p>"
        )
        
        self.summary_label.setText(summary)


class OnboardingWizard(QWizard):
    """Wizard complet d'onboarding"""
    
    def __init__(self, parent=None, lang="en"):
        super().__init__(parent)
        self.i18n = I18nManager(lang)
        
        self.setWindowTitle(self.i18n.get("wizard_title"))
        self.setWizardStyle(QWizard.ModernStyle)
        self.setFixedSize(700, 500)
        
        # Ajouter les pages
        self.addPage(WelcomePage(self.i18n))
        self.app_page = AppSelectionPage(self.i18n)
        self.addPage(self.app_page)
        self.diff_page = DifficultyPage(self.i18n)
        self.addPage(self.diff_page)
        self.addPage(FinalPage(self, self.i18n))
        
        # Textes des boutons
        self.setButtonText(QWizard.NextButton, self.i18n.get("wizard_next"))
        self.setButtonText(QWizard.BackButton, self.i18n.get("wizard_back"))
        self.setButtonText(QWizard.FinishButton, self.i18n.get("wizard_finish"))
        self.setButtonText(QWizard.CancelButton, self.i18n.get("wizard_cancel"))
    
    def get_configuration(self):
        """Obtenir la configuration finale"""
        return {
            "blocked_apps": self.app_page.get_selected_apps(),
            "difficulty_mode": self.diff_page.get_difficulty(),
            "language": self.i18n.lang, # Garder la langue actuelle
            "first_run": False,
            "custom_apps": []
        }


# Test standalone
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    # On peut tester en français en passant lang="fr"
    wizard = OnboardingWizard(lang="en")
    
    if wizard.exec() == QWizard.Accepted:
        config = wizard.get_configuration()
        print("Configuration:")
        print(f"  Blocked apps: {config['blocked_apps']}")
        print(f"  Difficulty: {config['difficulty_mode']}")
    else:
        print("Configuration annulée")
    
    sys.exit(0)
