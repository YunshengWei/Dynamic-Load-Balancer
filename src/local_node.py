import threading
import json
import logging
import Queue
import cPickle as pickle
from job import VectorAdditionTask, VectorAdditionJob
from worker_thread import worker
from state_manager import StateManager
from hardware_monitor import HardwareMonitor
from transfer_manager import TransferManager
from adaptor import Adaptor
from constant import *
from transfer_policy import *


class LocalNode:
    def __init__(self, workload):
        self.workload = workload
        self.state_manager = None
        self.hardware_monitor = None
        self.transfer_manager = None
        self.adaptor = None
        self.job_queue = Queue.Queue()
        self.completed_queue = Queue.Queue()

    def execute(self):
        self.state_manager = StateManager((LOCAL_HOST, STATE_MANAGER_PORT))
        self.hardware_monitor = HardwareMonitor()
        self.transfer_manager = TransferManager("HTTP://%s:%s/" % (REMOTE_HOST, TRANSFER_MANAGER_PORT),
                                                self.job_queue, self.completed_queue)

        self.transfer_manager.give_task()

        self._bootstrap()
        self._process()
        self._aggregate()

    def _bootstrap(self):
        my_workload, your_workload = self.workload.halve()
        self.transfer_manager.give_task(pickle.dumps(your_workload))

        for job in my_workload.split_into_jobs(NUM_CHUNK):
            self.job_queue.put(job)

        logging.info("Bootstrap phase finished")

    def _process(self):
        self.adaptor = Adaptor(self.state_manager, self.hardware_monitor,
                               self.transfer_manager, vanilla_transfer_policy())

        worker_thread = threading.Thread(target=worker,
                                         args=(self.job_queue, self.adaptor, self.completed_queue))
        worker_thread.daemon = True
        worker_thread.start()


        # Add a barrier for processing phase
        logging.info("Processing phase finished")

    def _aggregate(self):
        remote_results = pickle.loads(self.transfer_manager.fetch_result())

        while not self.completed_queue.empty():
            result = self.completed_queue.get_nowait()
            self.workload.fill_in_result(result)
        for result in remote_results:
            self.workload.fill_in_result(result)

        with open(RESULT_OUTPUT_FILE, 'w') as f:
            json.dump(self.workload.vector, f)

        logging.info("Aggregation phase finished")



if __name__ == "__main__":
    LocalNode(VectorAdditionTask()).execute()