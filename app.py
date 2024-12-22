from flask import Flask
from sqlalchemy import text
from models import db, bcrypt
from config import Config
from routes.auth import auth_bp 
from routes.main import main_bp 

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)


    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
