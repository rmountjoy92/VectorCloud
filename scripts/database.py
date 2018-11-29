#!/usr/bin/env python3

from flask_login import UserMixin
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

curr_path = os.path.dirname(__file__)
curr_path = os.path.abspath(os.path.join(curr_path, '..'))
db_path = os.path.join(curr_path, 'vectorcloud', 'site.db')

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path

# ------------------------------------------------------------------------------
# Import from the following
# ------------------------------------------------------------------------------

# main database instance
db = SQLAlchemy(app)


# database models (tables are built from the models)
class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    command = db.Column(db.Text)

    def __repr__(self):
        return self.command


class Output(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    output = db.Column(db.Text)

    def __repr__(self):
        return self.output


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return self.username


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script_name = db.Column(db.Text)
    description = db.Column(db.Text)
    icon = db.Column(db.String(20))
    hex_id = db.Column(db.Text)

    def __repr__(self):
        return [self.id, self.script_name, self.description, self.hex_id]


class AppSupport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hex_id = db.Column(db.Text)
    file_name = db.Column(db.Text)

    def __repr__(self):
        return [self.id, self.hex_id, self.file_name]


class Status(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Text)
    battery_voltage = db.Column(db.Float)
    battery_level = db.Column(db.Integer)
    status_charging = db.Column(db.Boolean)
    cube_battery_level = db.Column(db.Integer)
    cube_id = db.Column(db.Text)
    cube_battery_volts = db.Column(db.Float)
    timestamp = db.Column(db.Integer)

    def __repr__(self):
        return [self.id, self.battery_voltage, self.battery_level,
                self.status_charging, self.cube_battery_level,
                self.cube_id, self.cube_battery_volts, self.timestamp]


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    greeting_message_enabled = db.Column(db.Boolean, default=True)
    custom_greeting_message = db.Column(db.Text, default='default')

    def __repr__(self):
        return [self.id, self.greeting_message_enabled,
                self.custom_greeting_message]
