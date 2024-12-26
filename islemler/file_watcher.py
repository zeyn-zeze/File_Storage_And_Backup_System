from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from multiprocessing import Process
from islemler.backup_sync import backup_and_sync_with_progress

from threading import Lock

class FileWatcherHandler(FileSystemEventHandler):
    def __init__(self, source_dir, target_dir):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.lock = Lock()  # Kilit mekanizması

    def on_modified(self, event):
        print(f"Modified: {event.src_path}")
        self.trigger_backup()

    def on_created(self, event):
        print(f"Created: {event.src_path}")
        self.trigger_backup()

    def on_deleted(self, event):
        print(f"Deleted: {event.src_path}")
        self.trigger_backup()

    def trigger_backup(self):
        # Eğer başka bir yedekleme işlemi çalışıyorsa yeni bir işlem başlatma
        if self.lock.locked():
            print("Yedekleme zaten çalışıyor. Bekleniyor...")
            return

        with self.lock:
            backup_and_sync_with_progress(self.source_dir, self.target_dir)

    


def watch_directory(source_dir, target_dir):
    observer = Observer()
    event_handler = FileWatcherHandler(source_dir, target_dir)
    observer.schedule(event_handler, path=source_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
