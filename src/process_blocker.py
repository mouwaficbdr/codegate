import psutil
import signal
import time
import threading
import os
import atexit

class ProcessBlocker:
    def __init__(self, blocked_apps=None):
        self.blocked_apps = blocked_apps if blocked_apps else []
        self.paused_pids = set()
        self.running = False
        self.monitor_thread = None
        self.on_block_callback = None
        
        # Safety net: Ensure all processes are resumed on exit
        atexit.register(self.unblock_all)

    def start(self):
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def stop(self):
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        self.unblock_all()

    def _monitor_loop(self):
        while self.running:
            self._scan_and_block()
            time.sleep(1.0) # Check every second

    def _scan_and_block(self):
        current_user = os.getlogin()
        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                # Only block processes owned by the current user
                if proc.info['username'] != current_user:
                    continue

                if proc.info['name'] in self.blocked_apps:
                    if proc.info['pid'] not in self.paused_pids:
                        self._block_process(proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

    def _block_process(self, proc):
        try:
            print(f"Blocking process: {proc.info['name']} (PID: {proc.info['pid']})")
            proc.send_signal(signal.SIGSTOP)
            self.paused_pids.add(proc.info['pid'])
            if self.on_block_callback:
                self.on_block_callback()
        except psutil.Error as e:
            print(f"Failed to block {proc.info['name']}: {e}")

    def unblock_all(self):
        """Resumes all paused processes."""
        for pid in list(self.paused_pids):
            try:
                proc = psutil.Process(pid)
                print(f"Unblocking process: {proc.name()} (PID: {pid})")
                proc.send_signal(signal.SIGCONT)
            except psutil.NoSuchProcess:
                pass
            except psutil.Error as e:
                print(f"Error unblocking PID {pid}: {e}")
        self.paused_pids.clear()

    def update_blocked_apps(self, new_list):
        self.blocked_apps = new_list
