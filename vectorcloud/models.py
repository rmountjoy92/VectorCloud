#!/usr/bin/env python3

from vectorcloud import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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
    author = db.Column(db.Text)
    website = db.Column(db.Text)
    description = db.Column(db.Text)
    icon = db.Column(db.String(20))
    hex_id = db.Column(db.Text)
    run_in_bkrd = db.Column(db.Boolean, default=False)
    pid = db.Column(db.Integer, default=None)

    def __repr__(self):
        return [self.id, self.script_name, self.author,
                self.website, self.description, self.icon, self.hex_id,
                self.run_in_bkrd, self.pid]


class AppSupport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hex_id = db.Column(db.Text)
    file_name = db.Column(db.Text)
    settings = db.Column(db.Text)

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
    timestamp = db.Column(db.Float)
    ip = db.Column(db.Text)
    name = db.Column(db.Text)
    serial = db.Column(db.Text, default=None)

    def __repr__(self):
        return [self.id, self.battery_voltage, self.battery_level,
                self.status_charging, self.cube_battery_level,
                self.cube_id, self.cube_battery_volts, self.timestamp]


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_run = db.Column(db.Boolean, default=True)
    greeting_message_enabled = db.Column(db.Boolean, default=True)
    custom_greeting_message = db.Column(db.Text, default='default')
    search_by_name = db.Column(db.Boolean, default=True)
    search_by_description = db.Column(db.Boolean, default=True)
    search_by_author = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return [self.id, self.first_run, self.greeting_message_enabled,
                self.custom_greeting_message, self.view, self.search_by_name,
                self.search_by_description, self.search_by_author]


class ApplicationStore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script_name = db.Column(db.Text)
    author = db.Column(db.Text)
    website = db.Column(db.Text)
    description = db.Column(db.Text)
    icon = db.Column(db.String(20))
    installed = db.Column(db.Boolean, default=False)
    zip_file = db.Column(db.Text)

    def __repr__(self):
        return [self.id, self.script_name, self.author,
                self.website, self.description, self.icon,
                self.installed, self.zip_file]


class Vectors(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    serial = db.Column(db.Text)
    cert = db.Column(db.Text)
    ip = db.Column(db.Text)
    name = db.Column(db.Text)
    guid = db.Column(db.Text)
    default = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return [self.id, self.cert, self.ip, self.name, self.guid]


class AnkiConf(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Text)
    password = db.Column(db.Text)
    serial = db.Column(db.Text)
    ip = db.Column(db.Text)
    name = db.Column(db.Text)

    def __repr__(self):
        return [self.id, self.email, self.password,
                self.serial, self.ip, self.name]


class AppPrompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    output = db.Column(db.Text)

    def __repr__(self):
        return [self.id, self.question, self.answer, self.hex_id]
