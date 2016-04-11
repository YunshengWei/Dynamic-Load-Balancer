import time


def worker(job_queue, adaptor, completed_queue):
    while True:
        job = job_queue.get(True)

        start_time = time.time()
        job.compute()
        completed_queue.put(job)
        processing_time = time.time() - start_time

        cpu_throttling_value = adaptor.get_cpu_throttling()
        sleep_time = processing_time * (1 - cpu_throttling_value) / cpu_throttling_value
        if sleep_time > 0:
            time.sleep(sleep_time)
