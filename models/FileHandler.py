import os
from flask import current_app

class FileHandler:
    def __init__(self, app):
        self.app = app
        self.allowed_extensions = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

    def allowed_file(self, filename):
        """Dosya türünü kontrol eder"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.allowed_extensions

    def save_file(self, file):
        """Dosyayı belirlenen dizine kaydeder"""
        if file and self.allowed_file(file.filename):
            filename = os.path.join(self.app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            return filename
        return None
