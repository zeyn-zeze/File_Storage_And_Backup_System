import os
import glob
import time
from threading import Thread
from collections import defaultdict

from models.User import User
from utils.notifc import send_login_anomaly_notification

# Kullanıcı aktiviteleri için bir yapı
user_activity = defaultdict(list)

# İzlenecek log dizini
logs_directory = "./logs"

# Log Monitor Başlatma
def start_log_monitor(log_file):
    """Logs klasöründeki tüm .txt dosyalarını izleyen bir işlev"""
    log_files = glob.glob(os.path.join(logs_directory, "*.txt"))  # Tüm log dosyalarını bul
    log_file_handlers = {}

    # Mevcut log dosyalarını aç
    for log_file in log_files:
        log_file_handlers[log_file] = open(log_file, 'r')
        log_file_handlers[log_file].seek(0, 2)  # Dosyanın sonuna git

    print(f"{len(log_files)} log dosyası izleniyor...")

    while True:
        # Mevcut log dosyalarını oku
        for log_file, file_handler in log_file_handlers.items():
            line = file_handler.readline()
            if line:
                process_log_line(log_file, line)

        # Yeni dosyaları tespit et
        new_files = set(glob.glob(os.path.join(logs_directory, "*.txt"))) - set(log_file_handlers.keys())
        for new_file in new_files:
            print(f"Yeni log dosyası bulundu: {new_file}")
            log_file_handlers[new_file] = open(new_file, 'r')
            log_file_handlers[new_file].seek(0, 2)

        time.sleep(1)

# Log Satırlarını İşleme
def process_log_line(log_file, line):
    """Log satırlarını analiz eden işlev"""
    if "failed login" in line:
        handle_failed_login(log_file, line)
    elif "unexpected interruption" in line:
        handle_unexpected_interruption(log_file, line)
    elif "unauthorized access" in line:
        handle_unauthorized_access(log_file, line)
    elif "password change request" in line:
        handle_password_change_request(log_file, line)

# Anomali İşlevleri
def handle_failed_login(log_file, line):
    """Başarısız giriş denemelerini işler"""
    username = extract_username_from_log(line)
    if username:
        user_activity[username].append({"action": "failed_login", "timestamp": time.time()})
        failed_attempts = [action for action in user_activity[username] if action["action"] == "failed_login"]
        if len(failed_attempts) > 3:  # 3'ten fazla başarısız giriş
            print(f"Anormal durum: {username} kullanıcısı 3'ten fazla başarısız giriş denemesi yaptı!")

            # Kullanıcıyı ve admini bilgilendir
            user = User.query.filter_by(username=username).first()
            if user:
                send_login_anomaly_notification(
                    user=user,
                    message=f"{username} hesabında 3 başarısız giriş denemesi tespit edildi."
                )


def handle_unexpected_interruption(log_file, line):
    """Kesintileri işler"""
    print(f"Uyarı: Beklenmeyen kesinti tespit edildi -> {line.strip()}")
    log_anomaly(log_file, "Beklenmeyen kesinti")

def handle_unauthorized_access(log_file, line):
    """Yetkisiz erişimi işler"""
    print(f"Uyarı: Yetkisiz erişim tespit edildi -> {line.strip()}")
    log_anomaly(log_file, "Yetkisiz erişim")

def handle_password_change_request(log_file, line):
    """Parola değiştirme taleplerini işler"""
    username = extract_username_from_log(line)
    if username:
        user_activity[username].append({"action": "password_change", "timestamp": time.time()})
        recent_requests = [action for action in user_activity[username] if action["action"] == "password_change" and time.time() - action["timestamp"] < 300]
        if len(recent_requests) > 5:  # 5 dakika içinde 5'ten fazla talep
            print(f"Anormal durum: {username} kullanıcısı çok fazla parola değiştirme talebinde bulundu!")
            log_anomaly(log_file, f"{username} kullanıcısı parola değişikliği spam yaptı.")

# Kullanıcı Adını Log Satırından Çekme
def extract_username_from_log(line):
    """Log mesajından kullanıcı adını çıkarır"""
    if "Kullanıcı:" in line:
        return line.split("Kullanıcı:")[-1].strip()
    return None

# Anomali Loglama
def log_anomaly(log_file, message):
    """Anormal durumları loglar"""
    anomaly_log_path = "./logs/anomaly_logs.txt"
    with open(anomaly_log_path, "a") as anomaly_log:
        anomaly_log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Log: {log_file}, Anomaly: {message}\n")
