#!/usr/bin/env python3
"""
Notification Manager - Gestion des notifications système
Affiche des notifications pour les événements importants de CodeGate
"""

import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
import json


class NotificationManager:
    """Gestionnaire de notifications système via notify-send"""
    
    def __init__(self, app_name="CodeGate"):
        self.app_name = app_name
        self.stats_file = Path.home() / ".local" / "share" / "codegate" / "stats.json"
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Charger les stats
        self.stats = self._load_stats()
    
    def _load_stats(self) -> dict:
        """Charger les statistiques depuis le fichier"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except:
                return self._default_stats()
        return self._default_stats()
    
    def _default_stats(self) -> dict:
        """Statistiques par défaut"""
        return {
            "blocks_today": 0,
            "total_blocks": 0,
            "challenges_solved": 0,
            "challenges_failed": 0,
            "last_reset": datetime.now().strftime("%Y-%m-%d")
        }
    
    def _save_stats(self):
        """Sauvegarder les statistiques"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def _reset_daily_stats(self):
        """Réinitialiser les stats quotidiennes si nouveau jour"""
        today = datetime.now().strftime("%Y-%m-%d")
        if self.stats.get("last_reset") != today:
            self.stats["blocks_today"] = 0
            self.stats["last_reset"] = today
            self._save_stats()
    
    def send(self, title: str, message: str, urgency: str = "normal", icon: str = "security-high"):
        """
        Envoyer une notification système
        
        Args:
            title: Titre de la notification
            message: Message de la notification
            urgency: Niveau (low, normal, critical)
            icon: Nom de l'icône
        """
        try:
            subprocess.run([
                "notify-send",
                f"--app-name={self.app_name}",
                f"--urgency={urgency}",
                f"--icon={icon}",
                title,
                message
            ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except FileNotFoundError:
            # notify-send n'est pas installé
            print(f"[{self.app_name}] {title}: {message}")
    
    def notify_app_blocked(self, app_name: str):
        """Notification quand une app est bloquée"""
        self._reset_daily_stats()
        
        self.stats["blocks_today"] += 1
        self.stats["total_blocks"] += 1
        self._save_stats()
        
        self.send(
            "Application bloquée! 🔒",
            f"{app_name} a été bloquée.\nRésolvez le challenge pour continuer.",
            urgency="critical",
            icon="dialog-warning"
        )
    
    def notify_challenge_solved(self, language: str, time_taken: Optional[int] = None):
        """Notification quand un challenge est résolu"""
        self.stats["challenges_solved"] += 1
        self._save_stats()
        
        time_msg = f" en {time_taken}s" if time_taken else ""
        
        self.send(
            "Challenge résolu! ✅",
            f"Bravo! Challenge {language} résolu{time_msg}.\nVous avez accès à vos applications.",
            urgency="normal",
            icon="emblem-default"
        )
    
    def notify_challenge_failed(self):
        """Notification quand un challenge échoue"""
        self.stats["challenges_failed"] += 1
        self._save_stats()
        
        self.send(
            "Challenge échoué ❌",
            "Réessayez pour débloquer vos applications.",
            urgency="normal",
            icon="dialog-error"
        )
    
    def notify_startup(self):
        """Notification au démarrage de CodeGate"""
        self.send(
            "CodeGate actif",
            "La surveillance des applications est activée.",
            urgency="low",
            icon="security-high"
        )
    
    def notify_stats(self):
        """Notification avec les statistiques"""
        self._reset_daily_stats()
        
        message = (
            f"📊 Blocages aujourd'hui: {self.stats['blocks_today']}\n"
            f"🔒 Total blocages: {self.stats['total_blocks']}\n"
            f"✅ Challenges résolus: {self.stats['challenges_solved']}\n"
            f"❌ Challenges échoués: {self.stats['challenges_failed']}"
        )
        
        success_rate = 0
        total_challenges = self.stats['challenges_solved'] + self.stats['challenges_failed']
        if total_challenges > 0:
            success_rate = (self.stats['challenges_solved'] / total_challenges) * 100
            message += f"\n📈 Taux de réussite: {success_rate:.1f}%"
        
        self.send(
            "Statistiques CodeGate",
            message,
            urgency="low",
            icon="dialog-information"
        )
    
    def get_stats(self) -> dict:
        """Obtenir les statistiques actuelles"""
        self._reset_daily_stats()
        return self.stats.copy()


# Test du module
if __name__ == "__main__":
    nm = NotificationManager()
    
    print("Testing notifications...")
    
    # Test 1: App blocked
    nm.notify_app_blocked("Discord")
    
    # Test 2: Challenge solved
    import time
    time.sleep(2)
    nm.notify_challenge_solved("Python", time_taken=45)
    
    # Test 3: Stats
    time.sleep(2)
    nm.notify_stats()
    
    print("\n✓ Notifications sent!")
    print(f"Stats: {nm.get_stats()}")
