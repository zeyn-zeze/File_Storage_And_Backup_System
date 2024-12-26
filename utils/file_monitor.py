from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import os
import time
import schedule
from flask import current_app
from models import db
from models.File import File
from utils.backup_monitor import start_backup
from utils.config import source_directory,backup_directory

class FileMonitorHandler(FileSystemEventHandler):
    """Dosya değişikliklerini izleyen bir sınıf"""
    def on_modified(self, event):
        if not event.is_directory:
            print(f"Değişiklik algılandı: {event.src_path}")
            start_backup(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            print(f"Yeni dosya algılandı: {event.src_path}")
            start_backup(event.src_path)

def start_file_monitor(source_directory,backup_directory):
    """Dosya değişikliklerini izleyen proses"""
    event_handler = FileMonitorHandler()
    observer = Observer()
    observer.schedule(event_handler, source_directory, recursive=True)
    observer.start()
    print("Dosya izleme başlatıldı...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()



if not os.path.exists(source_directory):
    os.makedirs(source_directory)

if not os.path.exists(backup_directory):
    os.makedirs(backup_directory)
