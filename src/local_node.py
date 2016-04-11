import threading
import socket
import logging
from job import VectorAdditionTask, VectorAdditionJob

REMOTE_ADDRESS = ("cs423-s-gxx.cs.illinois.edu", 60000)


class LocalNode:
    def __init__(self, workload):
        self.workload = workload
        self.data_conn = None
        self.ctrl_conn = None
        self.job_queue = None
        self.result_list = []

    def execute(self):
        # remote stub
        self.remote = None
        # bootstrap phase
        self.bootstrap()
        # processing phase
        self.process()
        # aggregation phase
        self.aggregate()

    def bootstrap(self):
        pass

    def process(self):
        pass

    def aggregate(self):
        pass


if __name__ == "__main__":
    node = LocalNode(VectorAdditionTask())
    node.execute()