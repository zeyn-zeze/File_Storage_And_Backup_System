import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil
import os
from flask import current_app as app
from models import File, db
from datetime import datetime

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            print(f"Dosya değiştirildi: {event.src_path}")
            self.backup_file(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            print(f"Yeni dosya oluşturuldu: {event.src_path}")
            self.backup_file(event.src_path)

    def backup_file(self, file_path):
        filename = os.path.basename(file_path)
        backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backup')
        os.makedirs(backup_folder, exist_ok=True)
        backup_path = os.path.join(backup_folder, filename)

        if not os.path.exists(backup_path) or os.path.getmtime(file_path) > os.path.getmtime(backup_path):
            shutil.copy2(file_path, backup_path)
            print(f'{filename} yedeklendi.')

def start_watcher():
    watch_directory = app.config['UPLOAD_FOLDER']
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, watch_directory, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

