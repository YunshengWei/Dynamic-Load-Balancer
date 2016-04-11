class Adaptor:
    def __init__(self, state_manager, hardware_monitor, transfer_manager):
        self.sm= state_manager
        self.hm = hardware_monitor
        self.tm = transfer_manager

    