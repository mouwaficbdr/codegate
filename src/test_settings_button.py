#!/usr/bin/env python3
"""Script de test pour vérifier si le bouton paramètres fonctionne"""

import sys
import os

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PySide6.QtWidgets import QApplication, QPushButton, QMainWindow
from PySide6.QtGui import QIcon

app = QApplication(sys.argv)

window = QMainWindow()
window.setWindowTitle("Test Bouton Paramètres")

# Créer le bouton exactement comme dans le code
settings_btn = QPushButton()
icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "settings_icon.svg")
print(f"Chemin icône: {icon_path}")
print(f"Existe: {os.path.exists(icon_path)}")

if os.path.exists(icon_path):
    settings_btn.setIcon(QIcon(icon_path))
    print("Icône chargée")
else:
    settings_btn.setText("⚙")
    print("Fallback utilisé")

settings_btn.setFixedSize(32, 32)
settings_btn.setToolTip("Paramètres")

def test_click():
    print("✅ Bouton cliqué avec succès!")

settings_btn.clicked.connect(test_click)

window.setCentralWidget(settings_btn)
window.show()

print("Cliquez sur le bouton pour tester...")
sys.exit(app.exec())
