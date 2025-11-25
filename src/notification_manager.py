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
from src.i18n_manager import I18nManager


class NotificationManager:
    """Gestionnaire de notifications système via notify-send"""
    
    def __init__(self, app_name="CodeGate", lang="en"):
        self.app_name = app_name
        self.i18n = I18nManager(lang)
        self.stats_file = Path.home() / ".local" / "share" / "codegate" / "stats.json"
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Charger les stats
        self.stats = self._load_stats()
    
    def set_language(self, lang):
        """Mettre à jour la langue"""
        self.i18n.set_language(lang)

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
            self.i18n.get("notif_blocked_title"),
            self.i18n.get("notif_blocked_msg", app_name=app_name),
            urgency="critical",
            icon="dialog-warning"
        )
    
    def notify_challenge_solved(self, language: str, time_taken: Optional[int] = None):
        """Notification quand un challenge est résolu"""
        self.stats["challenges_solved"] += 1
        self._save_stats()
        
        time_msg = self.i18n.get("notif_time_msg", time_taken=time_taken) if time_taken else ""
        
        self.send(
            self.i18n.get("notif_solved_title"),
            self.i18n.get("notif_solved_msg", language=language, time_msg=time_msg),
            urgency="normal",
            icon="emblem-default"
        )
    
    def notify_challenge_failed(self):
        """Notification quand un challenge échoue"""
        self.stats["challenges_failed"] += 1
        self._save_stats()
        
        self.send(
            self.i18n.get("notif_failed_title"),
            self.i18n.get("notif_failed_msg"),
            urgency="normal",
            icon="dialog-error"
        )
    
    def notify_startup(self):
        """Notification au démarrage de CodeGate (cliquable)"""
        # Utiliser notify-send avec action pour ouvrir le dashboard
        try:
            # Version simple: notification cliquable avec action default
            subprocess.run([
                "notify-send",
                f"--app-name={self.app_name}",
                "--urgency=low",
                "--icon=security-high",
                "--action=default=Ouvrir le tableau de bord",
                self.i18n.get("notif_startup_title"),
                self.i18n.get("notif_startup_msg_clickable", 
                    "CodeGate est actif. Cliquez ici pour ouvrir le tableau de bord.")
            ], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            # Fallback: notification simple sans action
            self.send(
                self.i18n.get("notif_startup_title"),
                self.i18n.get("notif_startup_msg"),
                urgency="low",
                icon="security-high"
            )

    
    def notify_stats(self):
        """Notification avec les statistiques"""
        self._reset_daily_stats()
        
        message = (
            f"{self.i18n.get('notif_stats_blocks_today', count=self.stats['blocks_today'])}\n"
            f"{self.i18n.get('notif_stats_total_blocks', count=self.stats['total_blocks'])}\n"
            f"{self.i18n.get('notif_stats_solved', count=self.stats['challenges_solved'])}\n"
            f"{self.i18n.get('notif_stats_failed', count=self.stats['challenges_failed'])}"
        )
        
        success_rate = 0
        total_challenges = self.stats['challenges_solved'] + self.stats['challenges_failed']
        if total_challenges > 0:
            success_rate = (self.stats['challenges_solved'] / total_challenges) * 100
            message += f"\n{self.i18n.get('notif_stats_rate', rate=success_rate)}"
        
        self.send(
            self.i18n.get("notif_stats_title"),
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
    nm = NotificationManager(lang="en")
    
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
