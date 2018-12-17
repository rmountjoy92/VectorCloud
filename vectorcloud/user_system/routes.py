#!/usr/bin/env python3

import os
import signal
from flask import render_template, url_for, redirect, flash, Blueprint
from flask_login import login_user, logout_user, current_user
from vectorcloud.user_system.forms import RegisterForm, LoginForm
from vectorcloud.models import User, Application
from vectorcloud import db, bcrypt
from vectorcloud.main.utils import public_route
from vectorcloud.user_system.utils import login_message

user_system = Blueprint('user_system', __name__)

# ------------------------------------------------------------------------------
# User system routes
# ------------------------------------------------------------------------------

# registration page; when no users have been created (User table is empty)
# all pages will redirect to this page.


@public_route
@user_system.route("/register", methods=['GET', 'POST'])
def register():
    register.is_public = True
    user = User.query.first()

    if user:
        return redirect(url_for('user_system.login'))

    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Login Saved!", 'success')

        err_msg = login_message()
        if err_msg:
            return redirect(url_for('error_pages.' + err_msg))

        return redirect(url_for('user_system.login'))

    return render_template(
        'register.html', title='Register', form=form)


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
                return redirect(url_for('error_pages.' + err_msg))

            flash("Login Successful!", 'success')
            return redirect(url_for('main.home'))

        else:
            flash("Login Unsuccessful. Check username and password.",
                  'warning')
            return redirect(url_for('user_system.login'))

    return render_template(
        'login.html', title='Login', form=form)


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
