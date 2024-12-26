import shutil
from threading import Thread
import time
from utils.config import source_directory,backup_directory

import os

def backup_file(source_path, backup_path):
    """Dosyayı yedekler"""
    try:
        shutil.copy2(source_path, backup_path)
        print(f"Dosya yedeklendi: {source_path} -> {backup_path}")
    except Exception as e:
        print(f"Yedekleme hatası: {e}")

def start_backup(source_path,backup_path):
    """Dosya yedekleme işlemini bir thread ile başlatır"""
    try:
        # Kaynak dosya yolunu yedekleme diziniyle uyumlu hale getir
        relative_path = os.path.relpath(source_path, source_directory)
        backup_path = os.path.join(backup_directory, relative_path)

        # Yedekleme dizinindeki alt dizinlerin varlığını kontrol et ve oluştur
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)

        # Yedekleme işlemi için yeni bir thread başlat
        thread = Thread(target=backup_file, args=(source_path, backup_path), daemon=True)
        thread.start()
        thread.join()  # Opsiyonel: Yedekleme işleminin tamamlanmasını beklemek isterseniz bunu ekleyin

        print(f"Yedekleme başlatıldı: {source_path} -> {backup_path}")
    except Exception as e:
        print(f"Yedekleme başlatılırken hata oluştu: {e}")



def show_progress():
    """Yedekleme işlemlerinin ilerlemesini gösteren thread"""
    while True:
        time.sleep(5)
        total_files = len(os.listdir(source_directory))
        backed_up_files = len(os.listdir(backup_directory))
        print(f"İlerleme: {backed_up_files}/{total_files} dosya yedeklendi.")


