import socket
import time

from dotenv import load_dotenv

from app.core.config import settings
from app.services.call_processor import process_pending_task


load_dotenv()


def run_worker_loop() -> None:
    worker_id = f"worker-{socket.gethostname()}"
    print(f"[task_worker] started with worker_id={worker_id}")
    while True:
        try:
            processed = process_pending_task(worker_id)
            if processed:
                print(f"[task_worker] processed task_id={processed['task_id']} call_id={processed['call_id']}")
            else:
                time.sleep(settings.worker_poll_interval_seconds)
        except Exception as exc:
            print(f"[task_worker] task processing failed: {exc}")
            time.sleep(settings.worker_poll_interval_seconds)


if __name__ == "__main__":
    run_worker_loop()
