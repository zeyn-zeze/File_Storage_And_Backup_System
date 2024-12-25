from datetime import datetime
from models import db
from models import User  # User modelini içeri aktarın

class Folder(db.Model):
    __tablename__ = 'folders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    # İlişkiler
    user = db.relationship('User', backref='folders', lazy=True)
    files = db.relationship('File', backref='parent_folder', lazy=True)  # This is fine, as 'parent_folder' is now unique

    def __init__(self, owner_id, name, created_at):
        self.owner_id = owner_id
        self.name = name
        self.created_at = created_at

    def __repr__(self):
        return f'<Folder {self.name}>'


