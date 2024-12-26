import os
import shutil

from flask import app
from utils.utils import save_log  # save_log fonksiyonunu içeren dosyadan import edin
from models.File import File  # Veritabanı modellerinizden import edin
from models import db

def start_backup():
    """Tüm dosyalar için yedekleme işlemini başlatır."""
    files = File.query.all()
    for file in files:
        backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backup', file.folder.name)
        os.makedirs(backup_folder, exist_ok=True)
        backup_path = os.path.join(backup_folder, file.filename)

        # Eğer yedekleme dosyası yoksa ya da eskiyse, yedekle
        if not os.path.exists(backup_path) or os.path.getmtime(file.filepath) > os.path.getmtime(backup_path):
            shutil.copy2(file.filepath, backup_path)
            print(f"Yedeklendi: {file.filename}")
