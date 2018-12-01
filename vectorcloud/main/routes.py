#!/usr/bin/env python3

import sys
import time
import platform
from flask import render_template, url_for, redirect, flash, request, Blueprint
from flask_login import current_user
from vectorcloud.main.forms import CommandForm
from vectorcloud.models import Command, User, Status, Application
from vectorcloud.main.utils import robot_do, get_stats
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
global operating_system
global sdk_version
global vectorcloud_sdk_version
vectorcloud_sdk_version = "0.5.0"
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
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


# ------------------------------------------------------------------------------
# Home routes
# ------------------------------------------------------------------------------

# Home page


@main.route("/")
@main.route("/home", methods=['GET', 'POST'])
def home():
    if sdk_version != vectorcloud_sdk_version:
        flash('Incompatible SDK Version detected! ' + sdk_version +
              ' is installed. VectorCloud is using version: ' +
              vectorcloud_sdk_version, 'danger')
        return redirect(url_for('sdk_management.sdk'))

    app_list = Application.query.all()
    form = CommandForm()

    if form.validate_on_submit():
        robot_command = Command(command=form.command.data)
        db.session.add(robot_command)
        db.session.commit()
        return redirect(url_for('main.home'))

    command_list = Command.query.all()

    err_msg = get_stats()
    if err_msg:
        return redirect(url_for('error_pages.' + err_msg))

    vector_status = Status.query.first()
    return render_template('home.html', vector_status=vector_status,
                           form=form, command_list=command_list,
                           app_list=app_list)


# executes all commmands in the command table(if present), redirects to home.
@main.route("/execute_commands", methods=['GET', 'POST'])
def execute_commands():
    robot_commands = Command.query.all()
    if robot_commands:
        err_msg = robot_do()
        if err_msg:
            return redirect(url_for('error_pages.' + err_msg))

    else:
        flash('No command staged!', 'warning')

    return redirect(url_for('main.home'))


# clears the command table, redirects to home.
@main.route("/clear_commands")
def clear_commands():
    db.session.query(Command).delete()
    db.session.commit()
    return redirect(url_for('main.home'))


# adds undock command to the command table, runs robot_do(), redirects to home.
# this is a great example of how you can queue commands in the command table
# and execute them using robot_do (url /execute_commands)
@main.route("/undock")
def undock():
    db.session.query(Command).delete()
    robot_command = Command(command='robot.behavior.drive_off_charger()')
    db.session.add(robot_command)
    db.session.commit()

    err_msg = robot_do(override_output='Dock Command Complete!')
    if err_msg:
        db.session.query(Command).delete()
        db.session.commit()
        return redirect(url_for('error_pages.' + err_msg))

    err_msg = get_stats(force=True)
    if err_msg:
        return redirect(url_for('error_pages.' + err_msg))

    return redirect(url_for('main.home'))


# adds dock command to the command table, runs robot_do(), redirects to home.
@main.route("/dock")
def dock():
    db.session.query(Command).delete()
    robot_command = Command(command='robot.behavior.drive_on_charger()')
    db.session.add(robot_command)
    db.session.commit()

    err_msg = robot_do(override_output='Dock Command Complete!')
    if err_msg:
        db.session.query(Command).delete()
        db.session.commit()
        return redirect(url_for('error_pages.' + err_msg))

    err_msg = get_stats(force=True)
    if err_msg:
        return redirect(url_for('error_pages.' + err_msg))

    return redirect(url_for('main.home'))

# connects to cube to get data


@main.route("/connect_cube")
def connect_cube():
    db.session.query(Command).delete()
    robot_command = Command(command='robot.world.connect_cube()')
    db.session.add(robot_command)
    db.session.commit()

    err_msg = robot_do(override_output='Cube Connected!')
    if err_msg:
        return redirect(url_for('error_pages.' + err_msg))

    return redirect(url_for('main.home'))


# sends the following commands to Vector to attempt to pick up his cube
# redirects to home when done.
@main.route("/dock_cube")
def dock_cube():
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
        robot.behavior.drive_off_charger()
        cube = robot.world.connect_cube()
        if cube:
            robot.behavior.dock_with_cube(cube)
            robot.behavior.set_lift_height(100.0)
            time.sleep(5)
            robot.behavior.set_lift_height(0,  max_speed=10.0)
            robot.world.disconnect_cube()
            flash('Cube picked up!', 'success')
    return redirect(url_for('main.home'))
