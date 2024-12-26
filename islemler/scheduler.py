import time
import threading
from islemler.backup_sync import backup_and_sync_with_progress,source_directory,backup_directory
from islemler.log_monitor import search_keywords_in_logs


def schedule_tasks():
    print("Scheduler started.")
    while True:
        
        threading.Thread(target=backup_and_sync_with_progress, args=(source_directory, backup_directory)).start()
        #threading.Thread(target=search_keywords_in_logs, args=("log.txt", ["failed login", "error"])).start()
        time.sleep(60)  # Schedule tasks every minute


