#!/usr/bin/env python3
"""
Process Monitor - Détection améliorée des processus
Surveillance optimisée avec gestion des process trees
"""

import psutil
import os
from typing import Set, Dict, List


class ProcessMonitor:
    """Gestionnaire amélioré pour la détection et le suivi des processus"""
    
    def __init__(self):
        self.current_user = os.getlogin()
        self._process_cache = {}  # Cache pour éviter les lookups répétés
    
    def get_process_tree(self, pid: int) -> Set[int]:
        """
        Obtenir tous les PIDs d'un arbre de processus
        
        Args:
            pid: PID du processus parent
            
        Returns:
            Set de tous les PIDs (parent + enfants)
        """
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            
            pids = {pid}
            for child in children:
                pids.add(child.pid)
            
            return pids
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {pid}
    
    def find_processes_by_name(self, process_names: List[str]) -> Dict[str, List[int]]:
        """
        Trouver tous les PIDs correspondant aux noms de processus
        
        Args:
            process_names: Liste des noms de processus à chercher
            
        Returns:
            Dictionnaire {nom_process: [liste_de_pids]}
        """
        result = {name: [] for name in process_names}
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'exe']):
            try:
                # Filtrer par utilisateur
                if proc.info['username'] != self.current_user:
                    continue
                
                proc_name = proc.info['name']
                
                # Vérifier si le nom correspond
                if proc_name in process_names:
                    result[proc_name].append(proc.info['pid'])
                    continue
                
                # Vérifier aussi le chemin de l'exécutable
                # (pour détecter les apps renommées)
                exe = proc.info.get('exe', '')
                if exe:
                    exe_basename = os.path.basename(exe)
                    if exe_basename in process_names:
                        result[exe_basename].append(proc.info['pid'])
            
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        
        return result
    
    def is_process_running(self, process_name: str) -> bool:
        """
        Vérifier si un processus est en cours d'exécution
        
        Args:
            process_name: Nom du processus
            
        Returns:
            True si au moins une instance existe
        """
        for proc in psutil.process_iter(['name', 'username']):
            try:
                if proc.info['username'] == self.current_user and proc.info['name'] == process_name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return False
    
    def get_process_info(self, pid: int) -> Dict:
        """
        Obtenir les informations détaillées d'un processus
        
        Args:
            pid: PID du processus
            
        Returns:
            Dictionnaire avec les infos du processus
        """
        try:
            proc = psutil.Process(pid)
            return {
                'pid': pid,
                'name': proc.name(),
                'exe': proc.exe(),
                'cmdline': ' '.join(proc.cmdline()),
                'status': proc.status(),
                'create_time': proc.create_time(),
                'num_threads': proc.num_threads()
            }
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return {'pid': pid, 'error': 'Process not accessible'}
    
    def get_all_user_processes(self) -> List[Dict]:
        """
        Obtenir tous les processus de l'utilisateur courant
        
        Returns:
            Liste de dictionnaires avec les infos de chaque processus
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'username', 'exe']):
            try:
                if proc.info['username'] == self.current_user:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'exe': proc.info.get('exe', 'N/A')
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes


# Exemple d'utilisation
if __name__ == "__main__":
    monitor = ProcessMonitor()
    
    # Test 1: Chercher des processus spécifiques
    print("=== Test 1: Find processes ===")
    targets = ["python3", "firefox", "chrome"]
    found = monitor.find_processes_by_name(targets)
    for name, pids in found.items():
        if pids:
            print(f"{name}: {len(pids)} instance(s) - PIDs: {pids}")
    
    # Test 2: Vérifier si un processus tourne
    print("\n=== Test 2: Check if running ===")
    print(f"Python3 running: {monitor.is_process_running('python3')}")
    
    # Test 3: Arbre de processus
    print("\n=== Test 3: Process tree ===")
    if found['python3']:
        pid = found['python3'][0]
        tree = monitor.get_process_tree(pid)
        print(f"Process tree for PID {pid}: {tree}")
    
    # Test 4: Tous les processus utilisateur
    print("\n=== Test 4: All user processes ===")
    all_procs = monitor.get_all_user_processes()
    print(f"Total user processes: {len(all_procs)}")
    print("First 5:", all_procs[:5])
