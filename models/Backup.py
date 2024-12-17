import shutil
import os

class Backup:
    def __init__(self, source_dir, backup_dir):
        self.source_dir = source_dir  # Yedeklenecek dosyaların bulunduğu dizin
        self.backup_dir = backup_dir  # Yedeklerin kaydedileceği hedef dizin

    def backup_files(self):
        """Dosyaları kaynak dizinden hedef dizine yedekler"""
        try:
            files = self.find_files_in_directory(self.source_dir)
            for file in files:
                # Dosyanın hedef dizindeki yolunu oluştur
                target_path = os.path.join(self.backup_dir, os.path.relpath(file, self.source_dir))
                os.makedirs(os.path.dirname(target_path), exist_ok=True)  # Hedef dizini oluştur
                shutil.copy(file, target_path)
            return f"{len(files)} dosya başarıyla yedeklendi!"
        except Exception as e:
            return f"Yedekleme hatası: {e}"

    def find_files_in_directory(self, directory):
        """Verilen dizindeki tüm dosyaları arar ve listeler"""
        all_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                all_files.append(os.path.join(root, file))
        return all_files
