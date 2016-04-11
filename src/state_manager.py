class StateManager:
    def __init__(self, state_socket, hardware_monitor, job_queue):
        self.state_conn = state_socket
        self.hm = hardware_monitor
        self.job_queue = job_queue
