from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config

db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.routes import main, auth, moderator, users, movies, review
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(moderator.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(movies.bp)
    app.register_blueprint(review.bp)

    return app
