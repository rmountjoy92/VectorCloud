#!/usr/bin/env python3

from flask import render_template, url_for, redirect, flash, request, Blueprint
from flask_login import current_user
from vectorcloud.user_system.forms import RegisterForm
from vectorcloud.settings_system.forms import SettingsForms
from vectorcloud.models import User, Status, Settings
from vectorcloud.main.utils import get_stats
from vectorcloud.main.routes import sdk_version
from vectorcloud.application_store.utils import clear_temp_folder
from vectorcloud import db, bcrypt


settings_system = Blueprint('settings_system', __name__)


@settings_system.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response
    clear_temp_folder()
    return response


# ------------------------------------------------------------------------------
# Settings system routes
# ------------------------------------------------------------------------------

# settings pages
@settings_system.route("/settings", methods=['GET', 'POST'])
def settings():
    form = SettingsForms()
    settings_db = db.session.query(Settings).first()

    if settings_db is None:
        settings_db = Settings(greeting_message_enabled=True,
                               custom_greeting_message='Default')
        db.session.add(settings_db)
        db.session.commit()

    if form.validate_on_submit():
        settings_db = db.session.query(Settings).first()
        settings_db.greeting_message_enabled = \
            form.greeting_message_enabled.data
        settings_db.custom_greeting_message = form.custom_greeting_message.data
        msg = str(settings_db.custom_greeting_message)
        msg = msg.replace('%U', current_user.username)
        settings_db.custom_greeting_message = msg
        db.session.merge(settings_db)
        db.session.commit()
        flash('Settings Saved!', 'success')
        return redirect(url_for('settings_system.settings'))

    elif request.method == 'GET':
        form.custom_greeting_message.data = settings_db.custom_greeting_message
        form.greeting_message_enabled.data = settings_db.\
            greeting_message_enabled

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    return render_template('settings/main.html', form=form,
                           vector_status=vector_status,
                           sdk_version=sdk_version)


@settings_system.route("/settings_user", methods=['GET', 'POST'])
def settings_user():
    form = SettingsForms()
    user_form = RegisterForm()

    if user_form.validate_on_submit():
        current_user.username = user_form.username.data
        hashed_password = bcrypt.generate_password_hash(
            user_form.password.data).decode('utf-8')
        current_user.password = hashed_password
        flash('Login Credentials Updated!', 'success')
        db.session.commit()
        return redirect(url_for('settings_system.settings'))

    elif request.method == 'GET':
        user_form.username.data = current_user.username

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    return render_template('settings/user.html', form=form,
                           vector_status=vector_status,
                           user_form=user_form,
                           sdk_version=sdk_version)


# this clears the user table, redirects to register
@settings_system.route("/delete_user")
def delete_user():
    db.session.query(User).delete()
    db.session.commit()
    return redirect(url_for('user_system.register'))


@settings_system.route("/credits", methods=['GET', 'POST'])
def credits():

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    return render_template('settings/credits.html',
                           vector_status=vector_status,
                           sdk_version=sdk_version)
