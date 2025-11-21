#!/usr/bin/env python3
"""
Config Protector - Protection de l'intégrité de la configuration
Empêche les modifications non autorisées du fichier config.json
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigProtector:
    def __init__(self, config_path: str):
        """
        Args:
            config_path: Chemin vers config.json
        """
        self.config_path = Path(config_path)
        self.checksum_path = self.config_path.parent / ".config_checksum"
        
    def _calculate_checksum(self, data: Dict[str, Any]) -> str:
        """Calculer le SHA256 de la configuration"""
        # Normaliser pour un hash cohérent
        json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """
        Sauvegarder la configuration avec checksum
        
        Args:
            config: Configuration à sauvegarder
        """
        # Sauvegarder le fichier de config
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=4)
        
        # Calculer et sauvegarder le checksum
        checksum = self._calculate_checksum(config)
        with open(self.checksum_path, 'w') as f:
            f.write(checksum)
    
    def load_config(self, default_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Charger la configuration en vérifiant son intégrité
        
        Args:
            default_config: Configuration par défaut si fichier n'existe pas
            
        Returns:
            Configuration chargée ou par défaut
        """
        # Si le fichier n'existe pas, créer avec config par défaut
        if not self.config_path.exists():
            if default_config:
                self.save_config(default_config)
                return default_config
            else:
                raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        # Charger la configuration
        with open(self.config_path, 'r') as f:
            config = json.load(f)
        
        # Vérifier l'intégrité
        if not self.verify_integrity(config):
            print("⚠️  WARNING: Configuration file has been modified!")
            print("Possible tampering detected. Restoring from backup or defaults...")
            
            # Tenter de restaurer depuis le backup
            backup_config = self._try_restore_backup()
            if backup_config:
                print("✓ Restored from backup")
                self.save_config(backup_config)
                return backup_config
            elif default_config:
                print("✓ Using default configuration")
                self.save_config(default_config)
                return default_config
            else:
                print("⚠️  No backup available, using potentially tampered config")
                # Recalculer le checksum pour la config actuelle
                self.save_config(config)
                return config
        
        return config
    
    def verify_integrity(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Vérifier l'intégrité de la configuration
        
        Args:
            config: Configuration à vérifier (ou charge depuis le fichier)
            
        Returns:
            True si intègre, False sinon
        """
        # Si pas de checksum, considérer comme non vérifié
        if not self.checksum_path.exists():
            return False
        
        # Charger config si non fournie
        if config is None:
            if not self.config_path.exists():
                return False
            with open(self.config_path, 'r') as f:
                config = json.load(f)
        
        # Charger le checksum stocké
        with open(self.checksum_path, 'r') as f:
            stored_checksum = f.read().strip()
        
        # Calculer le checksum actuel
        current_checksum = self._calculate_checksum(config)
        
        return current_checksum == stored_checksum
    
    def create_backup(self) -> None:
        """Créer une sauvegarde de la configuration actuelle"""
        if not self.config_path.exists():
            return
        
        backup_path = self.config_path.parent / f"{self.config_path.name}.backup"
        
        # Copier le fichier
        import shutil
        shutil.copy2(self.config_path, backup_path)
        
        # Copier aussi le checksum
        if self.checksum_path.exists():
            backup_checksum_path = backup_path.parent / f".{backup_path.name}_checksum"
            shutil.copy2(self.checksum_path, backup_checksum_path)
    
    def _try_restore_backup(self) -> Optional[Dict[str, Any]]:
        """Tenter de restaurer la configuration depuis le backup"""
        backup_path = self.config_path.parent / f"{self.config_path.name}.backup"
        
        if not backup_path.exists():
            return None
        
        try:
            with open(backup_path, 'r') as f:
                backup_config = json.load(f)
            
            # Vérifier que le backup est valide
            backup_checksum_path = backup_path.parent / f".{backup_path.name}_checksum"
            if backup_checksum_path.exists():
                with open(backup_checksum_path, 'r') as f:
                    stored_checksum = f.read().strip()
                
                if self._calculate_checksum(backup_config) == stored_checksum:
                    return backup_config
            
            # Pas de checksum pour le backup, retourner quand même
            return backup_config
            
        except Exception as e:
            print(f"Failed to restore backup: {e}")
            return None
    
    def update_config(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mettre à jour la configuration avec protection
        
        Args:
            updates: Dictionnaire des mises à jour
            
        Returns:
            Configuration mise à jour
        """
        # Charger la config actuelle
        config = self.load_config()
        
        # Créer un backup avant modification
        self.create_backup()
        
        # Appliquer les mises à jour
        config.update(updates)
        
        # Sauvegarder avec nouveau checksum
        self.save_config(config)
        
        return config


# Exemple d'utilisation
if __name__ == "__main__":
    # Test
    protector = ConfigProtector("config.json")
    
    default_cfg = {
        "blocked_apps": ["discord", "firefox"],
        "language": "en",
        "difficulty_mode": "Mixed"
    }
    
    # Sauvegarder
    protector.save_config(default_cfg)
    print("✓ Config saved")
    
    # Charger et vérifier
    loaded = protector.load_config(default_cfg)
    print(f"✓ Config loaded: {loaded}")
    print(f"✓ Integrity verified: {protector.verify_integrity()}")
    
    # Simuler modification manuelle
    with open("config.json", 'w') as f:
        json.dump({"tampered": True}, f)
    
    print("\n--- After manual tampering ---")
    loaded = protector.load_config(default_cfg)
    print(f"✓ Config restored: {loaded}")
