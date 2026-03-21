import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'change-this-secret'

# Инициализируем расширения
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate(app, db)
login_manager.login_view = 'main.login'
login_manager.login_message = 'Пожалуйста, войдите в систему.'

db.init_app(app)
login_manager.init_app(app)

from .main import main
from .models import User
from .profile import profile

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app.register_blueprint(main)
app.register_blueprint(profile)