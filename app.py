from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from models.User import User
from routes.auth import auth_bp
from routes.main import main_bp
from routes.sync import sync_bp
from models import db, bcrypt

# LoginManager başlatıldıktan sonra user_loader fonksiyonunu tanımlayın
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # User modelindeki id ile kullanıcıyı yükle

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)

    # Initialize LoginManager
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(sync_bp)
    
    # Optional: You can set the login_view to the login route if necessary
    login_manager.login_view = 'auth.login'  # Login page for unauthenticated users

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
