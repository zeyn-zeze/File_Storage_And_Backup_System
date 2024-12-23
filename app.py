from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from models import db, bcrypt
from models.User import User
from routes.auth import auth_bp
from routes.main import main_bp
from routes.sync import sync_bp
from routes.team import team_bp
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(sync_bp)
    app.register_blueprint(team_bp)
    
    login_manager.login_view = 'auth.login'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
