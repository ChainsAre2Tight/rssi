import os
import sys
import time
import signal
import subprocess
import threading

from worker.registry import WORKERS


SHUTDOWN = False


def run_worker_loop(worker_name: str, module: str, instance: int):

    env = os.environ.copy()
    env["WORKER_NAME"] = f"{worker_name}-{instance}"

    while not SHUTDOWN:

        print(f"Starting worker {worker_name}-{instance}")

        process = subprocess.Popen(
            [sys.executable, "-m", module],
            env=env,
        )

        exit_code = process.wait()

        if SHUTDOWN:
            break

        print(
            f"Worker {worker_name}-{instance} exited with code {exit_code}, restarting..."
        )

        time.sleep(1)


def shutdown_handler(signum, frame):
    global SHUTDOWN
    print("Shutdown signal received")
    SHUTDOWN = True


def main():

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    threads = []

    for worker in WORKERS:

        for i in range(worker.instances):

            t = threading.Thread(
                target=run_worker_loop,
                args=(worker.name, worker.module, i),
                daemon=True,
            )

            t.start()
            threads.append(t)

    try:
        while not SHUTDOWN:
            time.sleep(1)

    except KeyboardInterrupt:
        shutdown_handler(None, None)

    print("Waiting for workers to stop...")

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()