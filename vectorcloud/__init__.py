#!/usr/bin/env python3

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_restful import Api


app = Flask(__name__)
api = Api(app)

app.config['SECRET_KEY'] = '66532a62c4048f976e22a39638b6f10e'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
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
from vectorcloud.manage_vectors.routes import manage_vectors

app.register_blueprint(main)
app.register_blueprint(user_system)
app.register_blueprint(application_system)
app.register_blueprint(settings_system)
app.register_blueprint(error_pages)
app.register_blueprint(flask_app)
app.register_blueprint(application_store)
app.register_blueprint(update_system)
app.register_blueprint(wiki_system)
app.register_blueprint(manage_vectors)

from vectorcloud.rest_api.resources import *

api.add_resource(UndockRobot, '/api/undock')
api.add_resource(DockRobot, '/api/dock')
api.add_resource(ConnectCube, '/api/connect_cube')
api.add_resource(DockCube, '/api/dock_cube')
api.add_resource(GetStatus, '/api/status')
api.add_resource(AddCommand, '/api/add_command')
api.add_resource(ExecuteCommands, '/api/execute')
api.add_resource(ClearCommands, '/api/clear_commands')
api.add_resource(RunApplication, '/api/run/<string:app_name>')
api.add_resource(ModRunApplication, '/api/modrun/<string:app_name>/<string:options>')
api.add_resource(ApplicationSettings, '/api/appset/<string:app_name>/<string:options>')
api.add_resource(GetVectors, '/api/vectors')
api.add_resource(ServerShutdown, '/api/server_shutdown')
api.add_resource(ServerReboot, '/api/server_reboot')
