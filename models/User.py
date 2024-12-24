from models import db, bcrypt
from flask_login import UserMixin

class User(db.Model, UserMixin):  # UserMixin burada ekleniyor
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(60), default='individual')  # 'individual' rolü varsayılan olarak atanacak
    storage_limit = db.Column(db.Integer, default=6144) 
    

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def generate_pass(self, password):
        # Ensure you are generating the password hash correctly
        if password:
            return bcrypt.generate_password_hash(password)
        return None  # This should never happen if the password is valid

    def get_id(self):
        return str(self.user_id)
