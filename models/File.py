from models import db
from models import User  # User modelini içeri aktarın

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # ForeignKey ile ilişki kurduk
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    # User ile ilişki tanımlanıyor
    user = db.relationship('User', backref='files', lazy=True)  # 'files' ismiyle geri ilişki

    def __init__(self, owner_id, filename, filepath, created_at):
        self.owner_id = owner_id
        self.filename = filename
        self.filepath = filepath
        self.created_at = created_at
