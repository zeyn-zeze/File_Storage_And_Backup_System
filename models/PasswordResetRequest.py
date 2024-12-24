from datetime import datetime
from models import db

class PasswordResetRequest(db.Model):
    __tablename__ = 'password_change_requests'  # Tablo adı

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    requested_at = db.Column(db.DateTime, nullable=False,default=datetime.now)
    status = db.Column(db.String(50), default = 'pending')
