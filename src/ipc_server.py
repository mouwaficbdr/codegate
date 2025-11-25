#!/usr/bin/env python3
"""
IPC Server - Serveur de communication inter-processus pour CodeGate
Permet aux commandes CLI de contrôler le daemon via socket Unix
"""

import os
import socket
import threading
import json
from pathlib import Path
from PySide6.QtCore import QObject, Signal


class IPCServer(QObject):
    """Serveur IPC écoutant sur un socket Unix"""
    
    # Signaux Qt pour communiquer avec le thread principal
    show_dashboard_signal = Signal()
    quit_signal = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Déterminer le chemin du socket (sécurisé)
        socket_dir = os.environ.get('XDG_RUNTIME_DIR')
        if not socket_dir:
            # Fallback sur ~/.cache/codegate
            socket_dir = Path.home() / '.cache' / 'codegate'
            Path(socket_dir).mkdir(parents=True, exist_ok=True)
        
        self.socket_path = Path(socket_dir) / 'codegate.sock'
        self.socket = None
        self.running = False
        self.server_thread = None
        
    def start(self):
        """Démarrer le serveur IPC"""
        # Nettoyer un éventuel socket existant
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except Exception as e:
                print(f"Warning: Could not remove old socket: {e}")
        
        # Créer le socket Unix
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.bind(str(self.socket_path))
            self.socket.listen(5)
            
            # Permissions: user only (600)
            self.socket_path.chmod(0o600)
            
            self.running = True
            
            # Lancer le thread serveur
            self.server_thread = threading.Thread(target=self._server_loop, daemon=True)
            self.server_thread.start()
            
            print(f"[IPC] Server started on {self.socket_path}")
            return True
            
        except Exception as e:
            print(f"[IPC] Failed to start server: {e}")
            return False
    
    def stop(self):
        """Arrêter le serveur IPC"""
        self.running = False
        
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        
        # Nettoyer le socket
        if self.socket_path.exists():
            try:
                self.socket_path.unlink()
            except:
                pass
        
        print("[IPC] Server stopped")
    
    def _server_loop(self):
        """Boucle principale du serveur (dans un thread)"""
        while self.running:
            try:
                # Accepter une connexion
                conn, _ = self.socket.accept()
                
                # Lire la commande
                data = conn.recv(1024).decode('utf-8').strip()
                
                # Traiter la commande
                response = self._handle_command(data)
                
                # Envoyer la réponse
                conn.sendall(response.encode('utf-8'))
                conn.close()
                
            except Exception as e:
                if self.running:
                    print(f"[IPC] Error in server loop: {e}")
    
    def _handle_command(self, command):
        """Traiter une commande IPC"""
        command = command.upper()
        
        if command == "SHOW_DASHBOARD":
            self.show_dashboard_signal.emit()
            return json.dumps({"status": "ok", "message": "Dashboard shown"})
        
        elif command == "QUIT":
            self.quit_signal.emit()
            return json.dumps({"status": "ok", "message": "Quitting"})
        
        elif command == "STATUS":
            return json.dumps({
                "status": "ok",
                "running": True,
                "pid": os.getpid()
            })
        
        else:
            return json.dumps({
                "status": "error",
                "message": f"Unknown command: {command}"
            })
    
    def __del__(self):
        """Destructeur: nettoyer le socket"""
        self.stop()
