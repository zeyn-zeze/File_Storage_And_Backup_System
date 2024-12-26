from datetime import datetime
from models import db

class Log(db.Model):
    __tablename__ = 'logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)  # Foreign key tanımlandı
    action_type = db.Column(db.String(50), nullable=False)
    action_details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    user = db.relationship('User', backref='logs', lazy=True)  # User modeli ile ilişki kuruldu

    def __repr__(self):
        return f"<Log {self.id}: {self.action_type} by User {self.user_id}>"
