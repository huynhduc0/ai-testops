import logging
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.core.management.base import BaseCommand
from api_tests.test_generator import run_test_case, save_test_result_to_db
from confluent_kafka import Producer
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

class TestFileChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.producer = Producer({'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS})

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            logging.debug(f"Detected change in {event.src_path}")
            result = run_test_case(event.src_path)
            test_case_id = int(event.src_path.split('_')[-1].split('.')[0])
            save_test_result_to_db(test_case_id, result['status'], result['log'])
            self.producer.produce('test_run_queue', event.src_path.encode('utf-8'))
            self.producer.flush()

def listen_for_file_changes():
    event_handler = TestFileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='test_cases', recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

class Command(BaseCommand):
    help = 'Start the file change listener'

    def handle(self, *args, **kwargs):
        listen_for_file_changes()
