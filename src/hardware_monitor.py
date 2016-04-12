import psutil
import threading
import sys
import logging


class HardwareMonitor:
    def __init__(self, cpu_throttling=1.0):
        self.cpu_throttling = cpu_throttling
        self.lock = threading.Lock()
        stdin_thread = threading.Thread(target=self.stdin_interface)
        stdin_thread.daemon = True
        stdin_thread.start()

    def get_cpu_throttling(self):
        with self.lock:
            return self.cpu_throttling

    def set_cpu_throttling(self, cpu_throttling):
        with self.lock:
            self.cpu_throttling = cpu_throttling

    def get_hardware_info(self):
        #todo
        pass

    def stdin_interface(self):
        while True:
            line = sys.stdin.readline().strip()
            if line.startswith("get"):
                print "Current cpu throttling value is %.2f%%" % self.get_cpu_throttling() * 100
            elif line.startswith("set"):
                value = float(line[3:])
                self.set_cpu_throttling(value)
                logging.info("Set cpu throttling value to %.2f%%" % value * 100)

