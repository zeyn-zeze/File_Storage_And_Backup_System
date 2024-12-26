import os
import time

def search_keywords_in_logs(logs_directory, keywords):
    """
    Logs klasöründeki tüm dosyaları izler ve belirtilen anahtar kelimeleri arar.
    """
    print(f"Monitoring log files in directory: {logs_directory}")
    
    if not os.path.exists(logs_directory):
        print(f"Directory not found: {logs_directory}")
        return

    file_positions = {}

    while True:
        try:
            # Tüm log dosyalarını kontrol et
            log_files = [f for f in os.listdir(logs_directory) if os.path.isfile(os.path.join(logs_directory, f))]

            for log_file in log_files:
                log_path = os.path.join(logs_directory, log_file)

                # Dosyayı aç ve anahtar kelimeleri tara
                with open(log_path, "r", encoding="utf-8") as f:
                    if log_path not in file_positions:
                        file_positions[log_path] = 0
                    
                    f.seek(file_positions[log_path])
                    
                    for line in f:
                        for keyword in keywords:
                            if keyword in line:
                                print(f"Keyword found: '{keyword}' in file: {log_file} | Line: {line.strip()}")

                    # İşlenen satır konumunu kaydet
                    file_positions[log_path] = f.tell()

            time.sleep(2)  # 2 saniye bekle ve tekrar kontrol et

        except Exception as e:
            print(f"Error while monitoring logs: {e}")
            time.sleep(5)
