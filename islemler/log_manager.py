import os
from datetime import datetime


class LogManager:
    def __init__(self, log_directory='logs', user_logs_directory='user_logs'):
        self.log_directory = log_directory
        self.user_logs_directory = user_logs_directory
        os.makedirs(self.log_directory, exist_ok=True)
        os.makedirs(self.user_logs_directory, exist_ok=True)

    def write_log(self, category, log_message, username=None):
        """
        Log yazma işlemi. Genel log ve kullanıcı bazlı loglara kaydeder.
        """
        # Genel log dosyasına kaydet
        general_log_path = os.path.join(self.log_directory, f"{category}.txt")
        with open(general_log_path, 'a') as general_log:
            general_log.write(log_message)

        # Kullanıcı bazlı log dosyasına kaydet
        if username:
            user_log_dir = os.path.join(self.user_logs_directory, username)
            os.makedirs(user_log_dir, exist_ok=True)  # Kullanıcı dizini yoksa oluştur
            user_log_path = os.path.join(user_log_dir, f"{category}.txt")
            with open(user_log_path, 'a') as user_log:
                user_log.write(log_message)

    def generate_log_message(self, start_time, end_time, operation_code, status_code, source_dir='-', data_size='-'):
        """
        Log mesajını oluşturur.
        """
        return f"{start_time}, {end_time}, {operation_code}, {status_code}, {source_dir}, {data_size}\n"

    def log_backup(self, source_dir, data_size, status_code="SUCCESS"):
        """
        Yedekleme işlemi için log kaydı.
        """
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = self.generate_log_message(
            start_time=start_time,
            end_time=end_time,
            operation_code="BACKUP",
            status_code=status_code,
            source_dir=source_dir,
            data_size=data_size
        )
        self.write_log(category="backup", log_message=log_message)

    def log_login(self, username, status_code="SUCCESS"):
        """
        Giriş işlemleri için log kaydı.
        """
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = self.generate_log_message(
            start_time=start_time,
            end_time=end_time,
            operation_code="LOGIN",
            status_code=status_code,
            source_dir=username,
            data_size="-"
        )
        self.write_log(category="login", log_message=log_message, username=username)

    def log_anomaly(self, username, description, status_code="DETECTED"):
        """
        Anormal durum tespiti için log kaydı.
        """
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = self.generate_log_message(
            start_time=start_time,
            end_time=end_time,
            operation_code="ANOMALY",
            status_code=status_code,
            source_dir="-",
            data_size=description
        )
        self.write_log(category="anomaly", log_message=log_message, username=username)

    def log_password_change_request(self, username, status_code="REQUESTED"):
        """
        Parola değiştirme talebi için log kaydı.
        """
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = self.generate_log_message(
            start_time=start_time,
            end_time=end_time,
            operation_code="PASSWORD_CHANGE_REQUEST",
            status_code=status_code,
            source_dir=username,
            data_size="-"
        )
        self.write_log(category="password_change", log_message=log_message, username=username)

    def log_password_change(self, username, status_code="SUCCESS"):
        """
        Başarılı parola değiştirme işlemi için log kaydı.
        """
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = self.generate_log_message(
            start_time=start_time,
            end_time=end_time,
            operation_code="PASSWORD_CHANGE",
            status_code=status_code,
            source_dir=username,
            data_size="-"
        )
        self.write_log(category="password_change_answer", log_message=log_message, username=username)

    def log_team_creation(self, username, team_name, member_usernames, status_code="SUCCESS"):
        """
        Takım oluşturma işlemi için log kaydı.
        """
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        members = ', '.join(member_usernames) if member_usernames else "No Members"
        log_message = self.generate_log_message(
            start_time=start_time,
            end_time=end_time,
            operation_code="TEAM_CREATION",
            status_code=status_code,
            source_dir=f"Team: {team_name}, Created by: {username}",
            data_size=f"Members: {members}"
        )
        self.write_log(category="team_creation", log_message=log_message, username=username)

    def log_file_upload(self, username, file_name, file_size, upload_dir, status_code="SUCCESS"):
        """
        Dosya yükleme işlemi için log kaydı.
        """
        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"{start_time}, {end_time}, FILE_UPLOAD, {status_code}, {upload_dir}/{file_name}, {file_size} bytes\n"
        self.write_log(category="file_upload", log_message=log_message, username=username)

    def log_post_creation(self, username, team_name, content, attached_file=None, status_code="SUCCESS"):

        start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_info = f", Attached File: {attached_file}" if attached_file else ""
        log_message = f"{start_time}, {end_time}, POST_CREATION, {status_code}, Team: {team_name}{file_info}, Content: {content}\n"
        self.write_log(category="post_creation", log_message=log_message, username=username)

