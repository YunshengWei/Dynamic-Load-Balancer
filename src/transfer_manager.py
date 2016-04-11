import Queue
import logging
import struct
import threading
from job import VectorAdditionJob


def receive_a_job(data_conn):
    buf = ""
    while len(buf) < 4:
        buf += data_conn.recv(4 - len(buf))
    length = struct.unpack("!I", buf)

    while len(buf) < length:
        buf += data_conn.recv(length - len(buf))
    return VectorAdditionJob.deserialize(buf)


class TransferManager:
    def __init__(self, data_conn, job_queue):
        self.data_conn = data_conn
        self.job_queue = job_queue
        receiver_thread = threading.Thread(target=self.job_receiver)
        receiver_thread.daemon = True
        receiver_thread.start()

    def load_transfer(self):
        try:
            job = self.job_queue.get(False)
            self.data_conn.sendall(job.serialize())
            logging.info("Transfer job [%s, %s]" % (job.start, job.end))
        except Queue.Empty as e:
            logging.debug("Error during load transfer: job queue is empty")

    def job_receiver(self):
        while True:
            job = receive_a_job(self.data_conn)
            logging.info("Receive job [%s, %s)" % (job.start, job.end))
            self.job_queue.put(job)