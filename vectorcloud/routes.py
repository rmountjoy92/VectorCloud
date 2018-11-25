#!/usr/bin/env python3

import os
import subprocess
import time
import secrets
from PIL import Image
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user, logout_user, current_user
import anki_vector
from anki_vector.util import degrees, radians
from vectorcloud.forms import CommandForm, RegisterForm, LoginForm,\
    UploadScript, SettingsForms
from vectorcloud.models import Command, Output, User, Application, AppSupport,\
    Status
from vectorcloud import app, db, bcrypt
import scripts


# ------------------------------------------------------------------------------
# intial routes and functions (before/after request)
# ------------------------------------------------------------------------------

# create all tables in the database if they don't exist
db.create_all()


# establishes routes decorated w/ @public_route as accessible while not signed
# in. See login and register routes for usage
def public_route(decorated_function):
    decorated_function.is_public = True
    return decorated_function


# blocks access to all pages (except public routes) unless the user is
# signed in.
@app.before_request
def check_valid_login():
    user = db.session.query(User).first()
    if any([request.endpoint.startswith('static'),
            current_user.is_authenticated,
            getattr(app.view_functions[request.endpoint],
                    'is_public', False)]):
        return
    elif user is None:
        return redirect(url_for('register'))
    else:
        return redirect(url_for('login'))


# this was a fix to make sure images stored in the cache are deleted when
# a new image is uploaded
@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


# ------------------------------------------------------------------------------
# Main functions
# ------------------------------------------------------------------------------

# get_stats(): this function gets the results of robot.get_version_state() &
# robot.get_battery_state() and stores it to the status table in the databse
# it clears the table at the begining of the function and leaves the data there
# until it is called again.
def get_stats():
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial, requires_behavior_control=False,
                           cache_animation_list=False) as robot:

        version_state = robot.get_version_state()
        battery_state = robot.get_battery_state()

        db.session.query(Status).delete()
        status = Status(version=version_state.os_version,
                        battery_voltage=battery_state.battery_volts,
                        battery_level=battery_state.battery_level,
                        status_charging=battery_state.is_on_charger_platform,
                        cube_battery_level=battery_state.cube_battery.level,
                        cube_id=battery_state.cube_battery.factory_id,
                        cube_battery_volts=battery_state.
                        cube_battery.battery_volts)
        db.session.add(status)
        db.session.commit()


# robot_do(): this function executes all commands in the command table in order
# with the condition of with anki_vector.Robot(args.serial) as robot:
# if there are commands in the commands in the command table, all you have to
# do to executes is redirect to /execute_commands/ and this function will be
# called.
def robot_do():
    robot_commands = Command.query.all()
    try:
        args = anki_vector.util.parse_command_args()
        with anki_vector.Robot(args.serial) as robot:
            for command in robot_commands:
                command_string = str(command)
                robot_output_string = str(eval(command_string))
                db_output = Output(output=robot_output_string)
                db.session.add(db_output)
                db.session.commit()
            command_output = Output.query.all()
            for out in command_output:
                out_string = str(out)
                flash(out_string, 'success')
    except NameError:
        flash('Command not found!', 'warning')
    db.session.query(Command).delete()
    db.session.query(Output).delete()
    db.session.commit()


# ------------------------------------------------------------------------------
# Home routes
# ------------------------------------------------------------------------------

# Home page
@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    try:
        app_list = Application.query.all()
        form = CommandForm()
        if form.validate_on_submit():
            robot_command = Command(command=form.command.data)
            db.session.add(robot_command)
            db.session.commit()
            return redirect(url_for('home'))
        command_list = Command.query.all()
        get_stats()
        vector_status = Status.query.first()
        return render_template('home.html', vector_status=vector_status,
                               form=form, command_list=command_list,
                               app_list=app_list)
    except anki_vector.exceptions.VectorNotFoundException:
        return redirect(url_for('vector_not_found'))


# executes all commmands in the command table(if present), redirects to home.
@app.route("/execute_commands")
def execute_commands():
    robot_commands = Command.query.all()
    if robot_commands:
        robot_do()
    else:
        flash('No command staged!', 'warning')
    return redirect(url_for('home'))


# clears the command table, redirects to home.
@app.route("/clear_commands")
def clear_commands():
    db.session.query(Command).delete()
    db.session.commit()
    return redirect(url_for('home'))


# sends undock commmand to Vector, waits for completion, redirects to home.
@app.route("/undock")
def undock():
    flash('Undock Command Complete!', 'success')
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
        robot.behavior.drive_off_charger()
    return redirect(url_for('home'))


# sends dock commmand to Vector, waits for completion, redirects to home.
@app.route("/dock")
def dock():
    flash('Dock Command Complete!', 'success')
    args = anki_vector.util.parse_command_args()
    try:
        with anki_vector.Robot(args.serial) as robot:
            robot.behavior.drive_on_charger()
            time.sleep(1)
        return redirect(url_for('home'))
    except anki_vector.exceptions.VectorControlTimeoutException:
        return redirect(url_for('vector_stuck'))


# sends the following commands to Vector to attempt to pick up his cube
# redirects to home when done.
@app.route("/dock_cube")
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
    return redirect(url_for('cube'))


# cube page
@app.route("/cube")
def cube():
    get_stats()
    vector_status = Status.query.first()
    return render_template(
        'cube.html', vector_status=vector_status, title='Cube')


# ------------------------------------------------------------------------------
# User system routes
# ------------------------------------------------------------------------------

# this makes Vector greet you when you log in from the login page
def login_message():
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
        robot.behavior.set_eye_color(hue=0.0, saturation=0.0)
        robot.say_text(current_user.username +
                       ' has logged in to Vector Cloud')


# registration page; when no users have been created (User table is empty)
# all pages will redirect to this page.
@public_route
@app.route("/register", methods=['GET', 'POST'])
def register():
    register.is_public = True
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data).decode('utf-8')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Login Saved!", 'success')
        return redirect(url_for('login'))
    return render_template(
        'register.html', title='Register', form=form)


# login page
@public_route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password,
                                               form.password.data):
            login_user(user, remember=form.remember.data)
            login_message()
            flash("Login Successful!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Check username and password.",
                  'warning')
            return redirect(url_for('login'))
    return render_template(
        'login.html', title='Login', form=form)


# this logs the user out and redirects to the login page
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


# ------------------------------------------------------------------------------
# Application system routes
# ------------------------------------------------------------------------------
# The upload system works as follows:
# 1. the upload page takes the form data and fills a row in the Application
#    table of the database.
#
# 2. the database columns that are created are:
#    id: unique key, assigned by the database (if it is the first app this = 1)
#    script_name: application's name given to it by the user
#    description: application's description given to it by the user
#    icon: application's icon file name (hex id + '.jpg' or '.png')
#    hex_id: application's hex id assigned to it from vectorcloud
#
# 3. main python file is renamed to (hex id + '.py') and saved to /scripts/
#
# 4. if added, the icon file is renamed to (hex id + '.jpg' or '.png') and
#    saved to static/app_icons/
#
# 5. if support files added, the upload page takes the form data and fills a
#    row in the AppSupport table of the database. The columns for each support
#    file created are:
#    id: unique key, assigned by the database
#    hex_id: the hex id of the application the file is related to
#    file_name: the file's name e.g. test.py
#
# 6. if added, support files are checked against existing entries and if unique
#    they are added to /scripts/lib


# this function takes the main python file from the form on the upload page,
# generates a hex id, renames the file with the hex id, saves the file to the
# scripts folder, then returns the hex id.
def save_script(form_script):
    random_hex = secrets.token_hex(8)
    file_name = random_hex + '.py'
    scripts_folder = os.path.dirname(scripts.__file__)
    script_path = os.path.join(scripts_folder, file_name)
    form_script.save(script_path)
    return random_hex


# this function takes one of the the support files from the form and the
# application's hex id, figures out if the file already exists in the lib
# package and if it doesn't, it adds the file to the lib package and registers
# it in the database.
def save_script_helpers(helper, random_hex):
    scripts_folder = os.path.dirname(scripts.__file__)
    lib_folder = scripts_folder + '/lib/'
    helper_name = str(helper)
    if len(helper_name) > 1:
        helper_name = helper_name.replace("<FileStorage: '", '')
        helper_name = helper_name.replace("' ('text/x-python')>", '')
        fn = os.path.join(lib_folder, helper_name)
        find_helper = AppSupport.query.filter_by(file_name=helper_name).first()
        if find_helper:
            is_in_db = True
        else:
            helper_db = AppSupport(hex_id=random_hex,
                                   file_name=helper_name)
            db.session.add(helper_db)
            is_in_db = False
            helper.save(fn)
            db.session.commit()
        return is_in_db
    else:
        pass


# this function takes the image file from the form on the upload page, and the
# application's hex id, renames the file with the hex id, saves the file to the
# static/app_icons folder, then returns the new file name.
def save_icon(form_icon, random_hex):
    _, f_ext = os.path.splitext(form_icon.filename)
    file_name = random_hex + f_ext
    icon_path = os.path.join(app.root_path, 'static/app_icons', file_name)

    output_size = (125, 125)
    i = Image.open(form_icon)
    i.thumbnail(output_size)
    i.save(icon_path)

    return file_name


# Upload page
@app.route("/upload", methods=['GET', 'POST'])
def upload():
    get_stats()
    vector_status = Status.query.first()
    form = UploadScript()
    if form.validate_on_submit():
        if form.script.data:
            random_hex = save_script(form.script.data)
            if form.script_helpers.data:
                for helper in form.script_helpers.data:
                    is_in_db = save_script_helpers(helper, random_hex)
                    if is_in_db is True:
                        flash("Helper File Already in Lib!", 'warning')
                        return redirect(url_for('upload'))
            if form.icon.data:
                icon_fn = save_icon(form.icon.data, random_hex)
            else:
                icon_fn = 'default.png'
            application = Application(hex_id=random_hex,
                                      script_name=form.script_name.data,
                                      description=form.description.data,
                                      icon=icon_fn)
            db.session.add(application)
            db.session.commit()
            flash("Application Saved!", 'success')
            return redirect(url_for('home'))
        else:
            flash("No script uploaded", 'warning')
        return redirect(url_for('upload'))
    return render_template(
        'upload.html', title='Upload', form=form, vector_status=vector_status)


# runs a script from the database by hex id. Hex id is passed into the url
# e.g. /run_script/cb893c1cee6d7e87 would run the script with hex id
# cb893c1cee6d7e87 in the database
@app.route("/run_script/<script_hex_id>")
def run_script(script_hex_id):
    application = Application.query.filter_by(hex_id=script_hex_id).first()
    scriptn = script_hex_id + '.py'
    scripts_folder = os.path.dirname(scripts.__file__)
    script_path = os.path.join(scripts_folder, scriptn)
    out = subprocess.run('python3 ' + script_path, stdout=subprocess.PIPE,
                         shell=True, encoding='utf-8')
    if out.returncode == 0:
        flash(application.script_name + ' ran succussfully! Output: ' +
              str(out.stdout), 'success')
    else:
        flash('Something is not right with your script.', 'warning')
    return redirect(url_for('home'))


# edit application page
@app.route("/edit_application/<script_id>", methods=['GET', 'POST'])
def edit_application(script_id):
    get_stats()
    vector_status = Status.query.first()
    form = UploadScript()
    application = Application.query.filter_by(id=script_id).first()
    support_files = AppSupport.query.filter_by(hex_id=application.hex_id)
    support_files_first = AppSupport.query.\
        filter_by(hex_id=application.hex_id).first()
    script_hex_id = application.hex_id

    if form.validate_on_submit():

        if form.script.data:
            scripts_folder = os.path.dirname(scripts.__file__)
            scriptn = script_hex_id + '.py'
            script_path = os.path.join(scripts_folder, scriptn)
            os.remove(script_path)
            form.script.data.save(script_path)

        if form.script_helpers.data:
            for helper in form.script_helpers.data:
                is_in_db = save_script_helpers(helper, script_hex_id)
                if is_in_db is True:
                    flash("Helper File Already in Lib!", 'warning')
                    return redirect(url_for('edit_application',
                                            script_id=script_id))

        if form.icon.data:
            if application.icon != 'default.png':
                icon_path = os.path.join(app.root_path,
                                         'static/app_icons', application.icon)
                os.remove(icon_path)

            icon_fn = save_icon(form.icon.data, script_hex_id)
            application.icon = icon_fn

        application.script_name = form.script_name.data
        application.description = form.description.data
        db.session.merge(application)
        db.session.commit()
        flash('Application Edited!', 'success')
        return redirect(url_for('edit_application', script_id=script_id))

    elif request.method == 'GET':
        form.script_name.data = application.script_name
        form.description.data = application.description

    return render_template(
        'edit_application.html', title='Edit Application', form=form,
        script_id=script_id, support_files=support_files,
        support_files_first=support_files_first, application=application,
        vector_status=vector_status)


# this deletes an application by it's unique key (id column). This will delete:
# 1. the main python file
# 2. image file (if not default)
# 3. any added support files associated with the hex id
# 4. database entries for all of the above
@app.route("/delete_application/<script_id>", methods=['GET', 'POST'])
def delete_application(script_id):
    application = Application.query.filter_by(id=script_id).first()
    hex_id = application.hex_id
    script_fn = application.hex_id + '.py'
    scripts_folder = os.path.dirname(scripts.__file__)
    script_path = os.path.join(scripts_folder, script_fn)
    icon_path = os.path.join(app.root_path,
                             'static/app_icons', application.icon)
    support_files = AppSupport.query.filter_by(hex_id=hex_id)
    lib_folder = scripts_folder + '/lib/'
    for file in support_files:
        file_path = lib_folder + file.file_name
        os.remove(file_path)
        AppSupport.query.filter_by(id=file.id).delete()
    os.remove(script_path)
    if application.icon != 'default.png':
        os.remove(icon_path)
    Application.query.filter_by(id=script_id).delete()
    db.session.commit()
    flash('Application Deleted!', 'success')
    return redirect(url_for('home'))


# this deletes a support file by it's unique key (id column).
# deletes the file from lib and removes databse entry
@app.route("/delete_support_file/<int:file_id>", methods=['GET', 'POST'])
def delete_support_file(file_id):
    support_file = AppSupport.query.filter_by(id=file_id).first()
    application = Application.query.\
        filter_by(hex_id=support_file.hex_id).first()
    scripts_folder = os.path.dirname(scripts.__file__)
    support_file_path = os.path.\
        join(scripts_folder, 'lib', support_file.file_name)
    os.remove(support_file_path)
    AppSupport.query.filter_by(id=file_id).delete()
    db.session.commit()
    flash(support_file.file_name + ' Deleted!', 'success')
    return redirect(url_for('edit_application', script_id=application.id))


# ------------------------------------------------------------------------------
# Settings system routes
# ------------------------------------------------------------------------------

# settings page
@app.route("/settings", methods=['GET', 'POST'])
def settings():
    form = SettingsForms()
    user_form = RegisterForm()
    if user_form.validate_on_submit():
        current_user.username = user_form.username.data
        hashed_password = bcrypt.generate_password_hash(
            user_form.password.data).decode('utf-8')
        current_user.password = hashed_password
        flash('Login Credentials Updated!', 'success')
        db.session.commit()
        return redirect(url_for('settings'))
    elif request.method == 'GET':
        user_form.username.data = current_user.username
    get_stats()
    vector_status = Status.query.first()
    return render_template('settings/user.html', form=form,
                           vector_status=vector_status, user_form=user_form)


# this clears the user table, redirects to register
@app.route("/delete_user")
def delete_user():
    db.session.query(User).delete()
    db.session.commit()
    return redirect(url_for('register'))


# ------------------------------------------------------------------------------
# Error Pages
# ------------------------------------------------------------------------------
@app.route("/vector_not_found")
def vector_not_found():
    return render_template('/error_pages/vector_not_found.html')


@app.route("/vector_stuck")
def vector_stuck():
    return render_template('/error_pages/vector_stuck.html')
