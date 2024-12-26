from datetime import datetime
from models import db  # db'yi app.py'den import ediyoruz

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # ForeignKey with correct table name
    message = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref='notifications', lazy=True)  # Relationship with User model

    def __repr__(self):
        return f'<Notification {self.message}>'


