import os
import shutil
from time import sleep
from threading import Thread, Lock
from datetime import datetime
from islemler.log_manager import LogManager  # LogManager'ı dahil edin

log_manager = LogManager()

class BackupSync:
    def __init__(self, source_dir, target_dir):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.total_files = 0
        self.completed = 0
        self.lock = Lock()  # İlerleme durumunu thread-safe yapmak için lock
        

    def backup_files(self):
        """
        Dosyaları yedekleme işlemi.
        """
        if not os.path.exists(self.source_dir):
            print("Kaynak dizin mevcut değil. Lütfen doğru bir kaynak dizin belirtin.")
            log_manager.log_backup(
                source_dir=self.source_dir,
                data_size="0",
                status_code="FAILED - Source directory does not exist"
            )
            return

        # Hedef dizin oluşturma
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)

        # Klasörleri ve dosyaları dolaşarak kopyalama işlemi
        self.total_files = sum([len(files) for _, _, files in os.walk(self.source_dir)])
        if self.total_files == 0:
            print("Kaynak dizin boş. Yedeklenecek dosya bulunamadı.")
            log_manager.log_backup(
                source_dir=self.source_dir,
                data_size="0",
                status_code="FAILED - Source directory is empty"
            )
            return

        print("Yedekleme işlemi başlatıldı...\n")
        log_manager.log_backup(
            source_dir=self.source_dir,
            data_size="0",
            status_code="STARTED"
        )

        for root, dirs, files in os.walk(self.source_dir):
            # Kaynak kök yolunu hedef kök yolu ile değiştir
            relative_path = os.path.relpath(root, self.source_dir)
            target_root = os.path.join(self.target_dir, relative_path)

            # Hedefteki klasörü oluştur
            if not os.path.exists(target_root):
                os.makedirs(target_root)

            # Dosyaları kopyala
            for filename in files:
                src_path = os.path.join(root, filename)  # Tam kaynak dosya yolu
                dest_path = os.path.join(target_root, filename)

                if os.path.isfile(src_path):
                    shutil.copy2(src_path, dest_path)
                    with self.lock:  # İlerleme durumunu güncellerken lock kullan
                        self.completed += 1

                    # Log dosyasına tam kaynak dosya yolunu ekle
                    log_manager.log_backup(
                        source_dir=src_path,  # Tam dosya yolu
                        data_size=f"{os.path.getsize(src_path)} bytes",
                        status_code=f"SUCCESS - File {filename} backed up"
                    )

                    sleep(0.2)  # Simülasyon için kısa bir bekleme süresi

        # Hedefte olup kaynakta olmayan dosyaları sil
        for root, dirs, files in os.walk(self.target_dir):
            relative_path = os.path.relpath(root, self.target_dir)
            source_root = os.path.join(self.source_dir, relative_path)

            if not os.path.exists(source_root):
                # Eğer kaynakta bu klasör yoksa, hedefteki klasörü sil
                shutil.rmtree(root)
                print(f"Silindi: {root}")
            else:
                # Eğer dosya kaynakta yoksa, hedefteki dosyayı sil
                for filename in files:
                    source_file = os.path.join(source_root, filename)
                    target_file = os.path.join(root, filename)
                    if not os.path.exists(source_file):
                        os.remove(target_file)
                        print(f"Silindi: {target_file}")

        print("\nYedekleme işlemi tamamlandı!")
        log_manager.log_backup(
            source_dir=self.source_dir,
            data_size=f"{self.completed} files",
            status_code="COMPLETED"
        )

    def show_progress(self):
        """
        İlerleme durumunu gösteren thread.
        """
        while self.completed < self.total_files:
            with self.lock:
                progress = (self.completed / self.total_files) * 100 if self.total_files > 0 else 0
                print(f"İlerleme: {progress:.2f}% - Tamamlanan Dosyalar: {self.completed}/{self.total_files}", end="\r")
                sleep(0.1)

        print("\nTüm dosyalar başarıyla yedeklendi!")


def backup_and_sync_with_progress(source_dir, target_dir):
    """
    Yedekleme işlemini ve ilerleme durumunu başlatır.
    """
    backup_sync = BackupSync(source_dir, target_dir)

    # Yedekleme thread'i
    backup_thread = Thread(target=backup_sync.backup_files)

    # İlerleme durumu thread'i
    progress_thread = Thread(target=backup_sync.show_progress)

    # Thread'leri başlat
    backup_thread.start()
    progress_thread.start()

    # Thread'lerin tamamlanmasını bekle
    backup_thread.join()
    progress_thread.join()


source_directory = 'uploads'
backup_directory = 'backups'

# Dizinleri kontrol edin ve yoksa oluşturun
os.makedirs(source_directory, exist_ok=True)
os.makedirs(backup_directory, exist_ok=True)


