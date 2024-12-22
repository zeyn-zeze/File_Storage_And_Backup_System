from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class File(db.Model):
    __tablename__ = 'files'  # Make sure this matches the table name in the database

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, owner_id, filename, filepath, created_at):
        self.owner_id = owner_id
        self.filename = filename
        self.filepath = filepath
        self.created_at = created_at
