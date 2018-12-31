#!/usr/bin/env python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)

app.config['SECRET_KEY'] = '66532a62c4048f976e22a39638b6f10e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)


from vectorcloud.main.routes import main
from vectorcloud.user_system.routes import user_system
from vectorcloud.application_system.routes import application_system
from vectorcloud.settings_system.routes import settings_system
from vectorcloud.error_pages.routes import error_pages
from vectorcloud.flask_app.routes import flask_app
from vectorcloud.application_store.routes import application_store
from vectorcloud.update_system.routes import update_system
from vectorcloud.wiki_system.routes import wiki_system

app.register_blueprint(main)
app.register_blueprint(user_system)
app.register_blueprint(application_system)
app.register_blueprint(settings_system)
app.register_blueprint(error_pages)
app.register_blueprint(flask_app)
app.register_blueprint(application_store)
app.register_blueprint(update_system)
app.register_blueprint(wiki_system)
