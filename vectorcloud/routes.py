#!/usr/bin/env python3

import multiprocessing
# import io
# import json
# import sys
# import os
import time
import anki_vector
from flask import render_template, url_for, redirect, flash, request
# from werkzeug.utils import secure_filename
# from PIL import Image
from vectorcloud.forms import CommandForm, RegisterForm, LoginForm
from vectorcloud.models import Command, Output
from vectorcloud import app, ALLOWED_EXTENSIONS, db
# from anki_vector import util


# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# VectorCloud code starts here
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------


output = multiprocessing.Queue()
global robot_commands
global command_output
robot_commands = []
command_output = []
db.create_all()


def get_stats(output):

    vector_status = {
        'status_version': '0',
        'status_voltage': '0',
        'status_battery_level': '0',
        'status_charging': '0',
        'status_cube_battery_level': '0',
        'status_cube_id': '0',
        'status_cube_battery_volts': '0'
    }

    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:

        version_state = robot.get_version_state()
        if version_state:
            vector_status['status_version'] = version_state.os_version

        battery_state = robot.get_battery_state()
        if battery_state:
            vector_status['status_voltage'] = battery_state.battery_volts
            vector_status['status_battery_level'] = battery_state.battery_level
            vector_status['status_charging'] = battery_state.is_on_charger_platform
            vector_status['status_cube_battery_level'] = battery_state.cube_battery.level
            vector_status['status_cube_id'] = battery_state.cube_battery.factory_id
            vector_status['status_cube_battery_volts'] = battery_state.cube_battery.battery_volts

        output.put(vector_status)


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


@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    form = CommandForm()
    if form.validate_on_submit():
        robot_command = Command(command=form.command.data)
        db.session.add(robot_command)
        db.session.commit()
        return redirect("/")
    command_list = Command.query.all()
    p = multiprocessing.Process(target=get_stats, args=(output,))
    p.start()
    vector_status = output.get()
    return render_template('home.html', vector_status=vector_status, form=form, command_list=command_list)
    p.join()


@app.route("/execute_commands")
def execute_commands():
    robot_commands = Command.query.all()
    if robot_commands:
        robot_do()
    else:
        flash('No command staged!', 'warning')
    return redirect("/")


@app.route("/clear_commands")
def clear_commands():
    db.session.query(Command).delete()
    db.session.commit()
    # db.drop_all()
    # db.create_all()
    return redirect("/")


@app.route("/undock")
def undock():
    flash('Undock Command Complete!', 'success')
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
        robot.behavior.drive_off_charger()
    return redirect("/")


@app.route("/dock")
def dock():
    flash('Dock Command Complete!', 'success')
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
        robot.behavior.drive_on_charger()
        time.sleep(1)
    return redirect("/")


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
    return redirect("/cube")


@app.route("/cube")
def cube():
    p = multiprocessing.Process(target=get_stats, args=(output,))
    p.start()
    vector_status = output.get()
    return render_template(
        'cube.html', vector_status=vector_status, title='Cube')
    p.join()


@app.route("/battery")
def battery():
    p = multiprocessing.Process(target=get_stats, args=(output,))
    p.start()
    vector_status = output.get()
    return render_template(
        'battery.html', vector_status=vector_status, title='Battery')
    p.join()


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        config_file = open("config.txt", "w")
        config_file.write(form.username.data + '\n' + form.password.data)
        config_file.close()
        flash("Login Saved!", 'success')
        return redirect(url_for('home'))
    return render_template(
        'register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Login Successful!", 'success')
        return redirect(url_for('home'))
    return render_template(
        'login.html', title='Login', form=form)

# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
# VectorCloud code ends here; Anki remote_control code Starts here.
# ------------------------------------------------------------------------------
# ------------------------------------------------------------------------------
