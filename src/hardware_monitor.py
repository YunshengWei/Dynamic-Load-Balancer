import psutil
import threading


class HardwareMonitor:
    def __init__(self, cpu_throttling=1.0):
        self.cpu_throttling = cpu_throttling
        self.lock = threading.Lock()

    def get_cpu_throttling(self):
        with self.lock:
            return self.cpu_throttling

    def set_cpu_throttling(self, cpu_throttling):
        with self.lock:
            self.cpu_throttling = cpu_throttling