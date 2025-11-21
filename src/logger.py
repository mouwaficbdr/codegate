#!/usr/bin/env python3
"""
Logger - Système de logging centralisé pour CodeGate
Gestion des logs avec rotation automatique et niveaux configurables
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


class CodeGateLogger:
    """Logger centralisé pour CodeGate avec rotation automatique"""
    
    # Niveaux de log
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    def __init__(self, name: str = "CodeGate", log_level: int = logging.INFO, verbose: bool = False):
        """
        Args:
            name: Nom du logger
            log_level: Niveau de log par défaut
            verbose: Mode verbose (affiche aussi sur console)
        """
        self.name = name
        self.verbose = verbose
        
        # Créer le dossier de logs
        self.log_dir = Path.home() / ".local" / "share" / "codegate" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Fichiers de log
        self.main_log = self.log_dir / "codegate.log"
        self.error_log = self.log_dir / "errors.log"
        
        # Créer le logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)
        
        # Éviter les doublons de handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Configurer les handlers de logging"""
        
        # Format des logs
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Handler 1: Fichier principal avec rotation (5 MB, 5 backups)
        file_handler = RotatingFileHandler(
            self.main_log,
            maxBytes=5 * 1024 * 1024,  # 5 MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Handler 2: Fichier d'erreurs uniquement
        error_handler = RotatingFileHandler(
            self.error_log,
            maxBytes=5 * 1024 * 1024,
            backupCount=3
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
        
        # Handler 3: Console (si verbose)
        if self.verbose:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
            console_formatter = logging.Formatter(
                fmt='[%(levelname)s] %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
    
    def debug(self, message: str, **kwargs):
        """Log niveau DEBUG"""
        self.logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log niveau INFO"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log niveau WARNING"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log niveau ERROR"""
        self.logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log niveau CRITICAL"""
        self.logger.critical(message, **kwargs)
    
    def exception(self, message: str, exc_info=True):
        """Log une exception avec traceback"""
        self.logger.exception(message, exc_info=exc_info)
    
    def log_event(self, event_type: str, details: dict):
        """
        Logger un événement structuré
        
        Args:
            event_type: Type d'événement (APP_BLOCKED, CHALLENGE_SOLVED, etc.)
            details: Dictionnaire avec les détails
        """
        import json
        message = f"EVENT:{event_type} {json.dumps(details)}"
        self.info(message)
    
    def get_recent_logs(self, lines: int = 50) -> list:
        """
        Obtenir les N dernières lignes de log
        
        Args:
            lines: Nombre de lignes à retourner
            
        Returns:
            Liste des lignes de log
        """
        try:
            with open(self.main_log, 'r') as f:
                return f.readlines()[-lines:]
        except FileNotFoundError:
            return []
    
    def get_recent_errors(self, lines: int = 20) -> list:
        """Obtenir les N dernières erreurs"""
        try:
            with open(self.error_log, 'r') as f:
                return f.readlines()[-lines:]
        except FileNotFoundError:
            return []
    
    def clear_logs(self):
        """Nettoyer tous les logs"""
        try:
            if self.main_log.exists():
                self.main_log.unlink()
            if self.error_log.exists():
                self.error_log.unlink()
            self.info("Logs cleared")
        except Exception as e:
            self.error(f"Failed to clear logs: {e}")
    
    @staticmethod
    def get_log_size(log_file: Path) -> str:
        """Obtenir la taille d'un fichier de log formatée"""
        if not log_file.exists():
            return "0 B"
        
        size = log_file.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def get_logs_info(self) -> dict:
        """Obtenir des informations sur les logs"""
        return {
            "main_log": {
                "path": str(self.main_log),
                "size": self.get_log_size(self.main_log),
                "exists": self.main_log.exists()
            },
            "error_log": {
                "path": str(self.error_log),
                "size": self.get_log_size(self.error_log),
                "exists": self.error_log.exists()
            }
        }


# Logger global pour l'application
_global_logger: Optional[CodeGateLogger] = None


def get_logger(name: str = "CodeGate", verbose: bool = False) -> CodeGateLogger:
    """
    Obtenir le logger centralisé
    
    Args:
        name: Nom du logger
        verbose: Mode verbose
        
    Returns:
        Instance du logger
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = CodeGateLogger(name, verbose=verbose)
    return _global_logger


# Test du module
if __name__ == "__main__":
    print("Testing logger...")
    
    # Créer un logger verbose
    logger = CodeGateLogger("TestLogger", verbose=True)
    
    # Tests
    logger.info("Application démarrée")
    logger.debug("Message de debug")
    logger.warning("Ceci est un avertissement")
    logger.error("Erreur de test")
    
    # Événement structuré
    logger.log_event("APP_BLOCKED", {
        "app_name": "Discord",
        "timestamp": datetime.now().isoformat()
    })
    
    # Tenter une exception
    try:
        raise ValueError("Test exception")
    except Exception:
        logger.exception("Une exception s'est produite")
    
    # Infos sur les logs
    print("\n=== Logs Info ===")
    import json
    print(json.dumps(logger.get_logs_info(), indent=2))
    
    print("\n=== Recent logs ===")
    for line in logger.get_recent_logs(5):
        print(line.strip())
    
    print("\n✓ Logger test complete!")
