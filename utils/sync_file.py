import os
import shutil


def sync_file(source_path, target_path):
     if not os.path.exists(target_path):
         shutil.copy2(source_path, target_path)
     else:
         # Dosya zaten mevcutsa, güncellenmişse kopyala
         if os.path.getmtime(source_path) > os.path.getmtime(target_path):
             shutil.copy2(source_path, target_path)
