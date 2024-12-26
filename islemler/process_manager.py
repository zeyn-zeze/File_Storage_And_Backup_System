from multiprocessing import Process

from islemler.anomaly_detection import detect_anomalies
from islemler.backup_sync import backup_and_sync_with_progress ,source_directory,backup_directory
from islemler.file_watcher import watch_directory
from islemler.log_monitor import search_keywords_in_logs
from islemler.scheduler import schedule_tasks
from islemler.user_behavior import analyze_user_behavior


def start_processes():
    """
    Tüm processleri başlatır.
    """
    
    
    processes = [
        Process(target=watch_directory, args=(source_directory, backup_directory)),  # Dosya İzleme
        Process(target=backup_and_sync_with_progress, args=(source_directory,backup_directory)),  # Yedekleme ve Senkronizasyon
        #Process(target=search_keywords_in_logs, args=("logs/login-logout.txt", ["failed login", "error"])),  # Log İzleme
        #Process(target=detect_anomalies, args=("login-logout.txt",)),  # Anomali Tespiti
       # Process(target=analyze_user_behavior, args=("login-logout.txt",)),  # Kullanıcı Davranışı Analizi
        Process(target=schedule_tasks)  # Periyodik Görevler
    ]

    for process in processes:
        process.start()

    return processes