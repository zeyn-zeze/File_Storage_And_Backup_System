from collections import defaultdict
import time
import re
from utils.analyze_log import handle_failed_login, handle_password_change_request

# Kullanıcı aktiviteleri için bir yapı
user_activity = defaultdict(list)

def monitor_user_activity(log_file_path):
    """Kullanıcı aktivitelerini analiz eden bir işlev"""
    try:
        with open(log_file_path, "r") as log_file:
            # Log dosyasını sürekli oku
            while True:
                line = log_file.readline()
                if not line:
                    time.sleep(1)  # Yeni bir log gelene kadar bekle
                    continue
                process_user_activity(line)
    except FileNotFoundError:
        print(f"Log dosyası bulunamadı: {log_file_path}")
    except Exception as e:
        print(f"Hata: {e}")

def process_user_activity(line):
    """Kullanıcı aktivitelerini işleyen bir işlev"""
    if "failed login" in line:
        handle_failed_login(line)
    elif "password change request" in line:
        handle_password_change_request(line)




def extract_username_from_log(line):
    """Log mesajından kullanıcı adını çıkarır"""
    match = re.search(r"Kullanıcı: (\w+)", line)
    if match:
        return match.group(1)
    return None

def log_anomaly(message):
    """Anomalileri log dosyasına kaydeder"""
    anomaly_log_path = "./logs/anomaly_logs.txt"
    with open(anomaly_log_path, "a") as log_file:
        log_file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
        
        
log_file_path = "./logs/user_logs.txt"