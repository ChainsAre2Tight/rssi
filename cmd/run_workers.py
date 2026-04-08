import os
import sys
import subprocess

from worker.registry import WORKERS


def start_worker(worker):

    env = os.environ.copy()
    env["WORKER_NAME"] = worker.name

    print(f"Starting worker: {worker.name}")

    return subprocess.Popen(
        [sys.executable, "-m", worker.module],
        env=env,
    )


def main():

    processes = []

    for worker in WORKERS:
        p = start_worker(worker)
        processes.append(p)

    try:
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("Stopping workers...")

        for p in processes:
            p.terminate()


if __name__ == "__main__":
    main()