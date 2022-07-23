from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

app = Flask("__name__")
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'
app.config['SECRET_KEY']='there is nthng secret abt this key'
db = SQLAlchemy(app)
db.init_app(app)

from website import routes
from website.models import User



login_manager = LoginManager()
login_manager.login_view = 'login_page'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def create_database(app):
    if not path.exists('website/database.db'):
        db.create_all(app=app)
        print('Created Database!')

create_database(app)