import signal
from threading import Event, Thread
import multiprocessing

multiprocessing.set_start_method('spawn', force=True)

from chonkie import MarkdownChef
from django.core.management.base import BaseCommand
from loguru import logger as log

stop_event = Event()

def collect_data():
    log.debug("Doing some chonkie stuff..")

    chef = MarkdownChef()
    log.debug(f"chef: {dir(chef)}")

    log.debug("Done doing chunking!")



def runner():
    while not stop_event.is_set():
        collect_data()
        break
        stop_event.wait(5)


class Command(BaseCommand):
    help = "Run text chunker"

    def handle(self, *args, **options):
        def handle_signal(signum, frame):
            log.info(f"Received termination signal ({signum}), shutting down...")
            stop_event.set()
            raise SystemExit(0)

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)

        bgworker = Thread(target=runner)
        log.info("New data will be fetched in background...")
        bgworker.start()

        try:
            while bgworker.is_alive():
                bgworker.join(timeout=1)
        except Exception:
            log.exception("Unexpected error in poster runner.")
        finally:
            stop_event.set()
            bgworker.join()
            log.info("Worker stopped cleanly.")
