#!/usr/bin/env python3

import os
import sys
import platform
from flask import render_template, url_for, redirect, flash, request, Blueprint
from flask_login import current_user
from vectorcloud.main.forms import CommandForm, SearchForm
from vectorcloud.models import Command, User, Status, Application, Output,\
    ApplicationStore, Settings
from vectorcloud.main.utils import execute_db_commands, get_stats,\
    undock_robot, dock_robot, robot_connect_cube
from vectorcloud.application_store.utils import clear_temp_folder
from vectorcloud.paths import temp_folder
from vectorcloud import db, app

try:
    import anki_vector
except ImportError:
    sys.exit("Cannot import from anki_vector: Install per Anki instructions")

main = Blueprint('main', __name__)

# ------------------------------------------------------------------------------
# intial routes and functions (before/after request)
# ------------------------------------------------------------------------------

# get the operating system & SDK version
vectorcloud_sdk_version = "0.5.1"
sdk_version = anki_vector.__version__
operating_system = platform.system()

# create all tables in the database if they don't exist
db.create_all()


# blocks access to all pages (except public routes) unless the user is
# signed in.


@main.before_request
def check_valid_login():
    user = db.session.query(User).first()

    if any([request.endpoint.startswith('static'),
            current_user.is_authenticated,
            getattr(app.view_functions[request.endpoint],
                    'is_public', False)]):
        return

    elif user is None:
        return redirect(url_for('user_system.register'))

    else:
        return redirect(url_for('user_system.login'))


# this was a fix to make sure images stored in the cache are deleted when
# a new image is uploaded
@main.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response
    clear_temp_folder()
    return response


# ------------------------------------------------------------------------------
# Home routes
# ------------------------------------------------------------------------------

# Home page
@main.route("/")
@main.route("/home", methods=['GET', 'POST'])
def home():
    settings = Settings.query.first()
    search_term = None
    num_results = 0

    if sdk_version != vectorcloud_sdk_version:
        flash('You are using a different version of the SDK than VectorCloud!\
               You are using ' + sdk_version + ' VectorCloud is using ' +
              vectorcloud_sdk_version, 'warning')

    temp_exists = os.path.isdir(temp_folder)
    if temp_exists is False:
        os.mkdir(temp_folder)

    output = Output.query.all()
    for out in output:
        flash(out, 'success')
    db.session.query(Output).delete()
    db.session.commit()

    app_list = Application.query.all()
    store_app_list = ApplicationStore.query.all()

    for store_app in store_app_list:
        for main_app in app_list:
            if store_app.script_name.lower() == main_app.script_name.lower():
                store_app.installed = True
                db.session.merge(store_app)
                db.session.commit()
            else:
                store_app.installed = False

    form = CommandForm()
    search_form = SearchForm()

    if form.validate_on_submit():
        robot_command = Command(command=form.command.data)
        db.session.add(robot_command)
        db.session.commit()
        return redirect(url_for('main.home'))

    if search_form.validate_on_submit():
        settings.search_by_name = search_form.by_name.data
        settings.search_by_description = search_form.by_description.data
        settings.search_by_author = search_form.by_author.data
        db.session.merge(settings)
        db.session.commit()
        search_term = search_form.search.data
        apps_searched = []

        if search_form.by_name.data is True:
            for application in app_list:
                if search_term.lower() in application.script_name.lower():
                    apps_searched.append(application.script_name)

        if search_form.by_description.data is True:
            for application in app_list:
                if search_term.lower() in application.description.lower():
                    apps_searched.append(application.script_name)

        if search_form.by_author.data is True:
            for application in app_list:
                if search_term.lower() in application.author.lower():
                    apps_searched.append(application.script_name)

        app_list = Application.query\
            .filter(Application.script_name.in_(apps_searched))
        apps_searched = set(apps_searched)
        num_results = len(apps_searched)

    elif request.method == 'GET':
        search_form.by_name.data = settings.search_by_name
        search_form.by_description.data = settings.search_by_description
        search_form.by_author.data = settings.search_by_author

    command_list = Command.query.all()

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()

    return render_template('home.html',
                           vector_status=vector_status,
                           form=form, command_list=command_list,
                           app_list=app_list,
                           sdk_version=sdk_version,
                           search_form=search_form,
                           search_term=search_term,
                           num_results=num_results)


# executes all commmands in the command table(if present), redirects to home.
@main.route("/execute_commands", methods=['GET', 'POST'])
def execute_commands():
    err_msg = execute_db_commands()

    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    return redirect(url_for('main.home'))


# clears the command table, redirects to home.
@main.route("/clear_commands")
def clear_commands():
    db.session.query(Command).delete()
    db.session.commit()
    return redirect(url_for('main.home'))


# adds undock command to the command table, runs robot_do(), redirects to home.
@main.route("/undock")
def undock():
    undock_robot()
    return redirect(url_for('main.home'))


# adds dock command to the command table, runs robot_do(), redirects to home.
@main.route("/dock")
def dock():
    dock_robot()
    return redirect(url_for('main.home'))


# connects to cube to get data
@main.route("/connect_cube")
def connect_cube():
    robot_connect_cube()
    return redirect(url_for('main.home'))
