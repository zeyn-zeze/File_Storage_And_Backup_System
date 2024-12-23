from datetime import datetime
from models import db

class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    members = db.relationship('TeamMember', back_populates='team', cascade="all, delete-orphan")
    posts = db.relationship('Post', back_populates='team', cascade="all, delete-orphan")
