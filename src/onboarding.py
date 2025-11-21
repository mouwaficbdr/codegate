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


class WelcomePage(QWizardPage):
    """Page d'accueil du wizard"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Bienvenue dans CodeGate! ⚡")
        
        layout = QVBoxLayout()
        
        # Message de bienvenue
        welcome_text = QLabel(
            "<h2>CodeGate - Productivité par le Code</h2>"
            "<p>CodeGate est un outil de productivité unique qui vous aide à rester concentré.</p>"
            "<br>"
            "<p><b>Comment ça marche?</b></p>"
            "<ol>"
            "<li>Vous sélectionnez les applications qui vous distraient</li>"
            "<li>Quand vous essayez de les ouvrir, elles sont <b>bloquées</b></li>"
            "<li>Vous devez <b>résoudre un challenge de code</b> pour y accéder</li>"
            "<li>Une fois résolu, vous avez accès jusqu'à la prochaine tentative</li>"
            "</ol>"
            "<br>"
            "<p>📚 <b>Bénéfices:</b></p>"
            "<ul>"
            "<li>✅ Amélioration de vos compétences en programmation</li>"
            "<li>✅ Réduction des distractions</li>"
            "<li>✅ Discipline personnelle renforcée</li>"
            "</ul>"
        )
        welcome_text.setWordWrap(True)
        welcome_text.setTextFormat(Qt.RichText)
        
        layout.addWidget(welcome_text)
        self.setLayout(layout)


class AppSelectionPage(QWizardPage):
    """Page de sélection des applications à bloquer"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Sélection des Applications")
        self.setSubTitle("Choisissez les applications que vous voulez bloquer")
        
        layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Sélectionnez les applications que vous trouvez <b>distrayantes</b> "
            "et pour lesquelles vous devrez résoudre un challenge avant d'y accéder."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Liste d'applications populaires
        self.app_list = QListWidget()
        
        # Applications courantes
        common_apps = {
            "Navigateurs": ["firefox", "chrome", "chromium", "brave"],
            "Communication": ["discord", "slack", "telegram", "signal"],
            "Jeux & Divertissement": ["steam", "spotify"],
            "Réseaux Sociaux": ["whatsapp", "thunderbird"]
        }
        
        # Ajouter par catégorie
        for category, apps in common_apps.items():
            # Header de catégorie
            header_item = QListWidgetItem(f"📁 {category}")
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
        suggestion = QLabel(
            "💡 <i>Conseil: Commencez avec 2-3 applications pour tester le système.</i>"
        )
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
    
    def __init__(self):
        super().__init__()
        self.setTitle("Niveau de Difficulté")
        self.setSubTitle("Choisissez le niveau de vos challenges")
        
        layout = QVBoxLayout()
        
        explanation = QLabel(
            "Les challenges varient en difficulté. Vous pouvez changer ce paramètre à tout moment."
        )
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        
        # Options de difficulté
        self.easy_cb = QCheckBox("✅ Facile - Problèmes simples (début)")
        self.medium_cb = QCheckBox("🔸 Moyen - Challenges intermédiaires")
        self.hard_cb = QCheckBox("🔥 Difficile - Algorithmes avancés")
        self.mixed_cb = QCheckBox("🎲 Mixte - Tous les niveaux (recommandé)")
        
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
    
    def __init__(self, parent_wizard):
        super().__init__()
        self.wizard = parent_wizard
        self.setTitle("Configuration Terminée! 🎉")
        
        layout = QVBoxLayout()
        
        # Résumé
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        self.summary_label.setTextFormat(Qt.RichText)
        layout.addWidget(self.summary_label)
        
        # Auto-start info
        autostart_info = QLabel(
            "<p><b>⚙️ Démarrage automatique:</b><br>"
            "CodeGate démarrera automatiquement à chaque connexion pour surveiller vos applications.</p>"
            "<p><b>🔧 Paramètres:</b><br>"
            "Vous pouvez modifier vos préférences à tout moment via le bouton ⚙ dans l'interface principale.</p>"
        )
        autostart_info.setWordWrap(True)
        layout.addWidget(autostart_info)
        
        # Message final
        final_msg = QLabel(
            "<hr>"
            "<h3>Prêt à booster votre productivité? 🚀</h3>"
            "<p>Cliquez sur <b>Terminer</b> pour commencer!</p>"
        )
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
        
        apps_text = "<br>".join([f"  • {app}" for app in selected_apps]) if selected_apps else "  <i>Aucune application</i>"
        
        summary = (
            f"<p><b>📱 Applications bloquées ({len(selected_apps)}):</b><br>"
            f"{apps_text}</p>"
            f"<p><b>🎯 Difficulté:</b> {difficulty}</p>"
        )
        
        self.summary_label.setText(summary)


class OnboardingWizard(QWizard):
    """Wizard complet d'onboarding"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("CodeGate - Configuration Initiale")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setFixedSize(700, 500)
        
        # Ajouter les pages
        self.addPage(WelcomePage())
        self.app_page = AppSelectionPage()
        self.addPage(self.app_page)
        self.diff_page = DifficultyPage()
        self.addPage(self.diff_page)
        self.addPage(FinalPage(self))
        
        # Textes des boutons
        self.setButtonText(QWizard.NextButton, "Suivant →")
        self.setButtonText(QWizard.BackButton, "← Retour")
        self.setButtonText(QWizard.FinishButton, "Terminer")
        self.setButtonText(QWizard.CancelButton, "Annuler")
    
    def get_configuration(self):
        """Obtenir la configuration finale"""
        return {
            "blocked_apps": self.app_page.get_selected_apps(),
            "difficulty_mode": self.diff_page.get_difficulty(),
            "language": "fr",
            "first_run": False,
            "custom_apps": []
        }


# Test standalone
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    wizard = OnboardingWizard()
    
    if wizard.exec() == QWizard.Accepted:
        config = wizard.get_configuration()
        print("Configuration:")
        print(f"  Blocked apps: {config['blocked_apps']}")
        print(f"  Difficulty: {config['difficulty_mode']}")
    else:
        print("Configuration annulée")
    
    sys.exit(0)
