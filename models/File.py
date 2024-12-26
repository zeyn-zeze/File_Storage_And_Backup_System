from datetime import datetime
from models import db
from models import User  # User modelini içeri aktarın
from models import Folder  # Folder modelini içeri aktarın

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # User tablosuna foreign key
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # datetime.utcnow kullanımı
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)  # Folder tablosuna foreign key
    is_backed_up = db.Column(db.Boolean, default=False)  # Yedekleme durumu
    is_synced = db.Column(db.Boolean, default=False)  # Senkronizasyon durumu

    # İlişkiler
    user = db.relationship('User', backref='files', lazy=True)  # Kullanıcı ile ilişki
    folder = db.relationship('Folder', backref='folders', lazy=True)  # Klasör ile ilişki

    def __init__(self, owner_id, filename, filepath, size, folder_id=None, created_at=None):
        self.owner_id = owner_id
        self.filename = filename
        self.filepath = filepath
        self.size = size
        self.folder_id = folder_id
        self.created_at = created_at or datetime.utcnow()

    def __repr__(self):
        return f'<File {self.filename}>'
