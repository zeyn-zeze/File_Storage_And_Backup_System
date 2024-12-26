
import os
import time
import schedule
from utils.backup_monitor import start_backup
from utils.config import source_directory

def periodic_backup():
    """Belirli zaman dilimlerinde yedekleme başlatır"""
    print("Periyodik yedekleme başlatılıyor...")
    for file_name in os.listdir(source_directory):
        source_path = os.path.join(source_directory, file_name)
        start_backup(source_path)

schedule.every(10).minutes.do(periodic_backup)

def start_scheduler():
    """Periyodik görevleri çalıştırır"""
    while True:
        schedule.run_pending()
        time.sleep(1)