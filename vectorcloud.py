#!/usr/bin/env python3

import anki_vector
import time
import multiprocessing
from flask import Flask, render_template, url_for, redirect

app = Flask(__name__)

output = multiprocessing.Queue()


def get_stats(output):
    vector_status = {
        'status_voltage': '0',
        'status_battery_level': '0',
        'status_charging': '0',
        'status_cube_battery_level': '0',
        'status_cube_id': '0',
        'status_cube_battery_volts': '0',
    }
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
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
@app.route("/home")
def home():
    p = multiprocessing.Process(target=get_stats, args=(output,))
    p.start()
    vector_status = output.get()
    return render_template('home.html', vector_status=vector_status)
    p.join()


@app.route("/undock")
def undock():
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
        robot.behavior.drive_off_charger()
    return redirect("/")


@app.route("/dock")
def dock():
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
        robot.behavior.drive_on_charger()
    return redirect("/")


@app.route("/control")
def control():
    return render_template('control.html', title='Control')


if __name__ == '__main__':

    app.run(use_reloader=True, debug=True)
