#!/usr/bin/env python3

import os
import subprocess
import signal
from flask import render_template, url_for, redirect, flash, Blueprint
from flask_login import login_user, logout_user, current_user
from platform import system as operating_system
from configparser import ConfigParser
from vectorcloud.user_system.forms import RegisterForm, LoginForm
from vectorcloud.models import User, Application, Settings, Vectors, AnkiConf
from vectorcloud import db, bcrypt
from vectorcloud.main.utils import public_route
from vectorcloud.manage_vectors.utils import init_vectors
from vectorcloud.user_system.utils import login_message
from vectorcloud.manage_vectors.forms import AddVector
from vectorcloud.paths import root_folder, sdk_config_file


user_system = Blueprint('user_system', __name__)

# ------------------------------------------------------------------------------
# User system routes
# ------------------------------------------------------------------------------


@public_route
@user_system.route("/welcome", methods=['GET', 'POST'])
def welcome():
    register.is_public = True

    form = AddVector()

    vectors = Vectors.query.all()

    settings = Settings.query.first()

    if form.validate_on_submit():
        anki_conf = AnkiConf(email=form.email.data,
                             password=form.password.data,
                             serial=form.vector_serial.data,
                             ip=form.vector_ip.data,
                             name=form.vector_name.data)

        db.session.add(anki_conf)
        db.session.commit()

        conf_path = os.path.join(root_folder, 'configure.py')
        if operating_system() == 'Windows':
            py_cmd = 'py '

        else:
            py_cmd = 'python3 '
        cmd = py_cmd + conf_path
        out = subprocess.run(cmd,
                             stdout=subprocess.PIPE,
                             shell=True,
                             encoding='utf-8')
        flash(str(out.stdout), 'success')

        init_vectors()

        top_vector = Vectors.query.first()
        if form.vector_serial.data == top_vector.serial:
            config = ConfigParser()
            config.read(sdk_config_file)
            config[top_vector.serial]['default'] = 'True'

            with open(sdk_config_file, 'w') as configfile:
                config.write(configfile)

        db.session.query(AnkiConf).delete()
        db.session.commit()
        return redirect(url_for('user_system.register'))

    settings.first_run = False
    db.session.merge(settings)
    db.session.commit()

    return render_template(
        'user/welcome.html', title='Welcome', vectors=vectors, form=form)


# registration page; when no users have been created (User table is empty)
# all pages will redirect to this page.
@public_route
@user_system.route("/register", methods=['GET', 'POST'])
def register():
    register.is_public = True
    user = User.query.first()
    settings = Settings.query.first()
    form = RegisterForm()

    if settings.first_run is True:
        return redirect(url_for('user_system.welcome'))

    elif current_user.is_authenticated:
        return redirect(url_for('main.home'))

    elif form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Login Saved!", 'success')

        err_msg = login_message()
        if err_msg:
            flash('No Vector is Connected. \
                Error message: ' + err_msg, 'warning')

        return redirect(url_for('user_system.login'))

    else:
        return render_template(
            'user/register.html', title='Register', form=form)


# login page
@public_route
@user_system.route("/login", methods=['GET', 'POST'])
def login():
    user = User.query.first()

    if user is None:
        return redirect(url_for('user_system.register'))

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):
            login_user(user, remember=form.remember.data)

            err_msg = login_message()
            if err_msg:
                flash('No Vector is Connected. \
                    Error message: ' + err_msg, 'warning')

            flash("Login Successful!", 'success')
            return redirect(url_for('main.home'))

        else:
            flash("Login Unsuccessful. Check username and password.",
                  'warning')
            return redirect(url_for('user_system.login'))

    return render_template(
        'user/login.html', title='Login', form=form)


# this logs the user out and redirects to the login page
@user_system.route("/logout")
def logout():
    applications = db.session.query(Application).\
        filter(Application.pid.isnot(None)).all()
    if len(applications) > 0:
        for application in applications:
            os.kill(int(application.pid), signal.SIGINT)
            application.pid = None
            db.session.merge(application)
            db.session.commit()
    logout_user()
    return redirect(url_for('user_system.login'))
