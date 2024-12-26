import os
import shutil
from threading import Thread
import time
from models import db
from flask import app, flash
from datetime import datetime

LOG_DIR = "logs"  # Log dosyalarının kaydedileceği dizin

def save_log(category, log_message):
    """
    Log mesajını belirli bir kategori altında bir .txt dosyasına kaydeder.
    :param category: Log kategorisi (örneğin: "giriş", "çıkış", "yedekleme")
    :param log_message: Kaydedilecek log mesajı
    """
    os.makedirs(LOG_DIR, exist_ok=True)  # Log dizini yoksa oluştur
    log_file_path = os.path.join(LOG_DIR, f"{category}.txt")

    # UTF-8 kodlamasıyla dosyayı açıyoruz
    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.now()} - {log_message}\n")


def backup_file(file_record):
    """Dosya yedekleme işlemi."""
    backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backup', file_record.folder.name)
    os.makedirs(backup_folder, exist_ok=True)
    backup_path = os.path.join(backup_folder, file_record.filename)

    try:
        # Yedekleme dosyası yoksa veya eski dosya daha yeni ise yedekle
        if not os.path.exists(backup_path) or os.path.getmtime(file_record.filepath) > os.path.getmtime(backup_path):
            shutil.copy2(file_record.filepath, backup_path)
            file_record.is_backup = 1  # Yedekleme tamamlandı, is_backup 1 yap
            db.session.commit()  # Veritabanına kaydet
            save_log("yedekleme", f"Yedekleme tamamlandı: {file_record.filename} - {datetime.now()}")
            print(f"Yedeklendi: {file_record.filename}")
    except Exception as e:
        save_log("anormallik", f"Yedekleme hatası: {file_record.filename} - {str(e)}")
        print(f"Yedekleme hatası: {e}")

def sync_file(file_record):
    """Dosya senkronizasyon işlemi."""
    try:
        source_path = file_record.filepath
        backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backup', file_record.folder.name)
        os.makedirs(backup_folder, exist_ok=True)
        backup_path = os.path.join(backup_folder, file_record.filename)

        # Yedekleme dizinindeki dosya ile kaynak dosya arasında senkronizasyonu sağla
        if not os.path.exists(backup_path) or os.path.getmtime(source_path) > os.path.getmtime(backup_path):
            shutil.copy2(source_path, backup_path)
            file_record.is_sync = 1  # Senkronizasyon tamamlandı, is_sync 1 yap
            db.session.commit()  # Veritabanına kaydet
            save_log("senkronizasyon", f"Senkronizasyon tamamlandı: {file_record.filename} - {datetime.now()}")
            print(f"Senkronizasyon tamamlandı: {source_path}")
    except Exception as e:
        save_log("anormallik", f"Senkronizasyon hatası: {file_record.filename} - {str(e)}")
        print(f"Senkronizasyon hatası: {e}")


