from datetime import datetime
from models import db
from models import User  # User modelini içeri aktarın
from models import Folder  # Folder modelini içeri aktarın
class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=True)
    size = db.Column(db.Integer, nullable=False)

    # İlişkiler
    user = db.relationship('User', backref='files', lazy=True)
    folder = db.relationship('Folder', backref='parent_files', lazy=True)  # Changed backref name to 'parent_files'

    def __init__(self, owner_id, filename, filepath, created_at, size, folder_id=None):
        self.owner_id = owner_id
        self.filename = filename
        self.filepath = filepath
        self.created_at = created_at
        self.size = size
        self.folder_id = folder_id

    def __repr__(self):
        return f'<File {self.filename}>'



