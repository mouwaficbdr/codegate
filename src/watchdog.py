#!/usr/bin/env python3
"""
Watchdog Process - Surveillance et relance automatique de CodeGate
Protège contre les tentatives de fermeture/kill du processus principal
"""

import os
import sys
import time
import psutil
import subprocess
import signal
from pathlib import Path


class CodeGateWatchdog:
    def __init__(self, target_script, check_interval=5):
        """
        Args:
            target_script: Chemin vers src/main.py
            check_interval: Intervalle de vérification en secondes
        """
        self.target_script = str(Path(target_script).resolve())
        self.check_interval = check_interval
        self.child_process = None
        self.restart_count = 0
        self.max_restarts_per_minute = 10
        self.restart_timestamps = []
        self.running = True
        
        # Log file
        log_dir = Path.home() / ".local" / "share" / "codegate" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = log_dir / "watchdog.log"
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _log(self, message):
        """Écrire dans le fichier de log"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}\n"
        print(log_msg.strip())
        
        try:
            with open(self.log_file, "a") as f:
                f.write(log_msg)
        except Exception as e:
            print(f"Failed to write to log: {e}")
    
    def _signal_handler(self, signum, frame):
        """Gestion des signaux pour arrêt propre"""
        self._log(f"Received signal {signum}, shutting down...")
        self.running = False
        if self.child_process and self.child_process.poll() is None:
            self._log("Terminating child process...")
            self.child_process.terminate()
            try:
                self.child_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._log("Child process didn't terminate, killing...")
                self.child_process.kill()
        sys.exit(0)
    
    def _check_restart_rate(self):
        """Vérifier si le taux de redémarrage est trop élevé"""
        now = time.time()
        # Garder seulement les timestamps de la dernière minute
        self.restart_timestamps = [ts for ts in self.restart_timestamps if now - ts < 60]
        
        if len(self.restart_timestamps) >= self.max_restarts_per_minute:
            self._log(f"ERROR: Too many restarts ({len(self.restart_timestamps)}) in the last minute!")
            self._log("Possible crash loop detected. Stopping watchdog.")
            return False
        
        self.restart_timestamps.append(now)
        return True
    
    def _start_child(self):
        """Démarrer le processus CodeGate"""
        try:
            # Obtenir le chemin du venv Python et le répertoire du projet
            project_root = Path(self.target_script).parent.parent
            venv_python = project_root / "venv" / "bin" / "python3"
            
            if venv_python.exists():
                python_cmd = str(venv_python)
            else:
                # Fallback sur python3 système
                python_cmd = sys.executable
            
            self._log(f"Starting CodeGate: {python_cmd} -m src.main")
            
            # Démarrer en arrière-plan avec le bon PYTHONPATH
            env = os.environ.copy()
            env['PYTHONPATH'] = str(project_root)
            
            self.child_process = subprocess.Popen(
                [python_cmd, "-m", "src.main"],
                cwd=str(project_root),  # Lancer depuis la racine du projet
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True  # Créer un nouveau group de processus
            )
            
            self.restart_count += 1
            self._log(f"CodeGate started with PID {self.child_process.pid} (restart #{self.restart_count})")
            return True
            
        except Exception as e:
            self._log(f"ERROR: Failed to start CodeGate: {e}")
            return False
    
    def _is_codegate_running(self):
        """Vérifier si le processus CodeGate est toujours actif"""
        if self.child_process is None:
            return False
        
        # Vérifier si le processus existe toujours
        poll_result = self.child_process.poll()
        
        if poll_result is not None:
            # Le processus s'est terminé
            self._log(f"CodeGate process terminated with exit code {poll_result}")
            
            # Lire stderr/stdout si disponible
            try:
                stderr = self.child_process.stderr.read().decode('utf-8', errors='ignore')
                if stderr:
                    self._log(f"STDERR: {stderr[:500]}")  # Limiter à 500 chars
            except:
                pass
            
            return False
        
        return True
    
    def run(self):
        """Boucle principale du watchdog"""
        self._log("="*50)
        self._log("CodeGate Watchdog started")
        self._log(f"Target script: {self.target_script}")
        self._log(f"Check interval: {self.check_interval}s")
        self._log("="*50)
        
        # Démarrage initial
        if not self._start_child():
            self._log("Failed to start CodeGate initially. Exiting.")
            return
        
        # Boucle de surveillance
        while self.running:
            time.sleep(self.check_interval)
            
            if not self._is_codegate_running():
                self._log("⚠️  CodeGate is not running! Attempting restart...")
                
                # Vérifier le taux de redémarrage
                if not self._check_restart_rate():
                    # Trop de redémarrages, arrêter le watchdog
                    self._log("Watchdog stopping due to crash loop.")
                    break
                
                # Redémarrer
                if not self._start_child():
                    self._log("Failed to restart CodeGate. Will retry next cycle.")
            else:
                # Tout va bien
                pass  # Log silencieux pour ne pas spammer
        
        self._log("Watchdog stopped")


def main():
    # Déterminer le chemin vers src/main.py
    watchdog_dir = Path(__file__).parent
    main_script = watchdog_dir / "main.py"
    
    if not main_script.exists():
        print(f"ERROR: Cannot find main.py at {main_script}")
        sys.exit(1)
    
    # Créer et lancer le watchdog
    watchdog = CodeGateWatchdog(main_script, check_interval=3)
    
    try:
        watchdog.run()
    except KeyboardInterrupt:
        print("\nWatchdog interrupted by user")
    except Exception as e:
        print(f"Watchdog crashed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
