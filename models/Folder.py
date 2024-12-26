from datetime import datetime
from models import db
from models import User  # User modelini içeri aktarın

class Folder(db.Model):
    __tablename__ = 'folders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # 'users' tablosuyla ilişki
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # İlişkiler
    user = db.relationship('User', backref='folders', lazy=True)  # Kullanıcı ile ilişki
    files = db.relationship('File', backref='file', lazy=True)  # Dosyalar ile ilişki

    def __init__(self, owner_id, name, created_at):
        self.owner_id = owner_id
        self.name = name
        self.created_at = created_at

    def __repr__(self):
        return f'<Folder {self.name}>'
