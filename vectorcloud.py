#!/usr/bin/env python3

from flask import Flask, render_template, url_for, redirect, flash
from forms import CommandForm
import multiprocessing
import time
import anki_vector


app = Flask(__name__)

app.config['SECRET_KEY'] = '66532a62c4048f976e22a39638b6f10e'

output = multiprocessing.Queue()


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


@app.route("/")
@app.route("/home", methods=['GET', 'POST'])
def home():
    form = CommandForm()
    if form.validate_on_submit():
        try:
            args = anki_vector.util.parse_command_args()
            with anki_vector.Robot(args.serial) as robot:
                command_output = eval(form.command.data)
            if command_output:
                command_output = str(command_output)
                flash(command_output, 'success')
        except NameError:
            flash('Command not found!', 'warning')
        return redirect("/")
    p = multiprocessing.Process(target=get_stats, args=(output,))
    p.start()
    vector_status = output.get()
    return render_template('home.html', vector_status=vector_status, form=form)
    p.join()


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


@app.route("/control")
def control():
    return render_template('control.html', title='Control')


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


if __name__ == '__main__':

    app.run(debug=True, use_reloader=True, host="0.0.0.0")
