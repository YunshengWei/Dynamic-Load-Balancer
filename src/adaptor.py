import time
from constant import *


class Adaptor:
    def __init__(self, state_manager, hardware_monitor, transfer_manager, transfer_policy):
        self.sm = state_manager
        self.hm = hardware_monitor
        self.tm = transfer_manager
        self.transfer_policy = transfer_policy

    def adapt(self):
        while True:
            remote_state = self.sm.get_remote_system_state()
            my_queue_size = self.tm.get_jobqueue_size()

            if remote_state is not None:
                if remote_state["pending_job"] == 0 and my_queue_size == 0:
                    self.tm.job_queue.join()
                    return
                else:
                    transfer_decision, extra_params = self.transfer_policy(\
                        remote_state, self.hm.get_hardware_info(), my_queue_size)
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

            time.sleep(ADAPTOR_PERIOD)

    def get_cpu_throttling(self):
        return self.hm.get_cpu_throttling()
