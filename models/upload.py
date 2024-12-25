import os
import shutil
from flask import current_app as app

def backup_file(src_path):
    # Yedekleme klasörünü belirle
    backup_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'backups')
    os.makedirs(backup_folder, exist_ok=True)

    # Dosyayı yedekle
    filename = os.path.basename(src_path)
    backup_path = os.path.join(backup_folder, filename)

    # Dosyayı yedekleme
    shutil.copy2(src_path, backup_path)
    print(f'{filename} yedeklendi.')
