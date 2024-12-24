from datetime import datetime
from models import db

class PasswordChangeRequest(db.Model):
    __tablename__ = 'password_change_requests'  # Tablo adı

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False) 
    requested_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    status = db.Column(db.String(50), default='pending', nullable=False)
    new_password = db.Column(db.String(255), nullable=False)  # Store the new password

    user = db.relationship('User', backref='password_change_requests', lazy=True)
