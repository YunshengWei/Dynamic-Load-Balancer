import threading
from constant import *


class Adaptor:
    def __init__(self, state_manager, hardware_monitor, transfer_manager, transfer_policy):
        self.sm = state_manager
        self.hm = hardware_monitor
        self.tm = transfer_manager
        self.transfer_policy = transfer_policy
        self.adapt_thread = None

    def adapt(self):
        with self.lock:
            if self.sm.get_remote_system_state() is not None:
                transfer_decision = self.transfer_policy(self.sm.get_remote_system_state(),
                                                         self.hm.get_hardware_info(),
                                                         self.tm.get_jobqueue_size())
                if transfer_decision is "None":
                    pass
                elif transfer_decision is "transfer":
                    self.tm.transfer_load()
                elif transfer_decision is "request":
                    self.tm.request_load()

            state = {"pending_job": self.tm.get_jobqueue_size(),
                     "cpu_throttling": self.hm.get_cpu_throttling(),
                     "hardware_info": self.hm.get_hardware_info()}
            self.sm.send_state(state)

            self.adapt_thread = threading.Timer(ADAPTOR_PERIOD, self.adapt)
            self.adapt_thread.daemon = True
            self.adapt_thread.start()

    def get_cpu_throttling(self):
        return self.hm.get_cpu_throttling()
