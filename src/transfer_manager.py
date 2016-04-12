import Queue
import threading
import xmlrpclib
import logging
import cPickle as pickle
from SimpleXMLRPCServer import SimpleXMLRPCServer
from constant import *


# def receive_a_job(data_conn):
#     buf = ""
#     while len(buf) < 4:
#         buf += data_conn.recv(4 - len(buf))
#     length = struct.unpack("!I", buf)
#
#     while len(buf) < length:
#         buf += data_conn.recv(length - len(buf))
#     return VectorAdditionJob.deserialize(buf)


class TransferManager:
    def __init__(self, remote_uri, job_queue, completed_queue):
        self.job_queue = job_queue
        self.completed_queue = completed_queue
        self.proxy = xmlrpclib.ServerProxy(remote_uri)
        self._set_up_rpc()

    def _set_up_rpc(self):
        server = SimpleXMLRPCServer(("", TRANSFER_MANAGER_PORT), allow_none=True)
        logging.info("Transfer manager listening on port %s..." % TRANSFER_MANAGER_PORT)

        server.register_function(self.give_task, "give_task")
        server.register_function(self.fetch_job, "fetch_job")
        server.register_function(self.give_job, "give_job")
        server.register_function(self.fetch_results, "fetch_results")

        rpc_server_thread = threading.Thread(target=lambda: server.serve_forever())
        rpc_server_thread.daemon = True
        rpc_server_thread.start()

    def transfer_load(self):
        try:
            job = self.job_queue.get(False)
            logging.info("Transfer job [%s, %s)" % (job.start, job.end))
            self.proxy.give_job(pickle.dumps(job))
            self.job_queue.task_done()
        except Queue.Empty as e:
            logging.debug("Error during load transfer: job queue is empty")

    def request_load(self):
        job = self.proxy.fetch_job()
        if job is not None:
            self.job_queue.put(job)
            logging.info("Receive job [%s, %s)" % (job.start, job.end))

    def transfer_workload(self, workload):
        task = pickle.dumps(workload)
        self.proxy.give_task(task)

    def collect_results(self):
        return self.proxy.fetch_results()

    def get_jobqueue_size(self):
        return self.job_queue.qsize()

    # def load_transfer(self):
    #     try:
    #         job = self.job_queue.get(False)
    #         self.data_conn.sendall(job.serialize())
    #         logging.info("Transfer job [%s, %s]" % (job.start, job.end))
    #     except Queue.Empty as e:
    #         logging.debug("Error during load transfer: job queue is empty")

    # def job_receiver(self):
    #     while True:
    #         job = receive_a_job(self.data_conn)
    #         logging.info("Receive job [%s, %s)" % (job.start, job.end))
    #         self.job_queue.put(job)

    def fetch_job(self):
        try:
            job = self.job_queue.get(False)
            self.job_queue.task_done()
            logging.info("Transfer job [%s, %s)" % (job.start, job.end))
            return pickle.dumps(job)
        except Queue.Empty as e:
            logging.debug("Error during load transfer: job queue is empty")

    def give_job(self, job):
        job = pickle.loads(job)
        logging.info("Receive job [%s, %s)" % (job.start, job.end))
        self.job_queue.put(job)

    def give_task(self, task):
        task = pickle.loads(task)
        logging.info("Receive workload, start: %s, size: %s" % (task.start, task.length))
        for job in task.split_into_jobs(NUM_CHUNK):
            self.job_queue.put(job)

    def fetch_results(self):
        self.job_queue.join()
        logging.info("Transferring results ...")
        # The function should only be called after processing phase finishes
        # So don't worry about more than one thread access completed_queue
        results = []
        while not self.completed_queue.empty():
            results.append(self.completed_queue.get_nowait())
        return pickle.dumps(results)
