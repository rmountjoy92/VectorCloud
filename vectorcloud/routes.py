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

db.create_all()


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


def public_route(decorated_function):
    decorated_function.is_public = True
    return decorated_function


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


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


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


@app.route("/vector_not_found")
def vector_not_found():
    return render_template('/error_pages/vector_not_found.html')


@app.route("/vector_stuck")
def vector_stuck():
    return render_template('/error_pages/vector_stuck.html')


@app.route("/execute_commands")
def execute_commands():
    robot_commands = Command.query.all()
    if robot_commands:
        robot_do()
    else:
        flash('No command staged!', 'warning')
    return redirect(url_for('home'))


@app.route("/clear_commands")
def clear_commands():
    db.session.query(Command).delete()
    db.session.commit()
    return redirect(url_for('home'))


@app.route("/undock")
def undock():
    flash('Undock Command Complete!', 'success')
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
        robot.behavior.drive_off_charger()
    return redirect(url_for('home'))


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


@app.route("/cube")
def cube():
    get_stats()
    vector_status = Status.query.first()
    return render_template(
        'cube.html', vector_status=vector_status, title='Cube')


@app.route("/battery")
def battery():
    get_stats()
    vector_status = Status.query.first()
    return render_template(
        'battery.html', vector_status=vector_status, title='Battery')


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
            flash("Login Successful!", 'success')
            return redirect(url_for('home'))
        else:
            flash("Login Unsuccessful. Check username and password.",
                  'warning')
            return redirect(url_for('login'))
    return render_template(
        'login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))


def save_script(form_script):
    random_hex = secrets.token_hex(8)
    file_name = random_hex + '.py'
    scripts_folder = os.path.dirname(scripts.__file__)
    script_path = os.path.join(scripts_folder, file_name)
    form_script.save(script_path)
    return random_hex


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


def save_icon(form_icon, random_hex):
    _, f_ext = os.path.splitext(form_icon.filename)
    file_name = random_hex + f_ext
    icon_path = os.path.join(app.root_path, 'static/app_icons', file_name)

    output_size = (125, 125)
    i = Image.open(form_icon)
    i.thumbnail(output_size)
    i.save(icon_path)

    return file_name


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


@app.route("/edit_application/<script_id>", methods=['GET', 'POST'])
def edit_application(script_id):
    get_stats()
    vector_status = Status.query.first()
    form = UploadScript()
    application = Application.query.filter_by(id=script_id).first()
    support_files = AppSupport.query.filter_by(hex_id=application.hex_id)
    support_files_first = AppSupport.query.filter_by(hex_id=application.hex_id).first()
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


@app.route("/delete_support_file/<int:file_id>", methods=['GET', 'POST'])
def delete_support_file(file_id):
    support_file = AppSupport.query.filter_by(id=file_id).first()
    application = Application.query.filter_by(hex_id=support_file.hex_id).first()
    scripts_folder = os.path.dirname(scripts.__file__)
    support_file_path = os.path.join(scripts_folder, 'lib', support_file.file_name)
    os.remove(support_file_path)
    AppSupport.query.filter_by(id=file_id).delete()
    db.session.commit()
    flash(support_file.file_name + ' Deleted!', 'success')
    return redirect(url_for('edit_application', script_id=application.id))


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


@app.route("/delete_user")
def delete_user():
    db.session.query(User).delete()
    db.session.commit()
    return redirect(url_for('register'))

# def run_rc():
#     scripts_folder = os.path.dirname(scripts.__file__)
#     rc_path = os.path.join(scripts_folder, 'remote_control', 'start.sh')
#     os.system(rc_path)
#     # rc_pid = p.pid
#     # db_pid = RC(pid=rc_pid)
#     # db.session.add(db_pid)
#     # db.session.commit()


# @app.route("/control", methods=['GET', 'POST'])
# def control():
#     # run_rc
#     # p = multiprocessing.Process(target=run_rc)
#     # p.start()
#     return render_template('control.html', title='Control')


# @app.route("/kill_control", methods=['GET', 'POST'])
# def kill_control():
#     # rc_pid = RC.query.all()
#     # os.kill(rc_pid, signal.SIGINT)
#     # db.session.query(RC).delete()
#     # db.session.commit()
#     # return redirect(url_for('home'))
