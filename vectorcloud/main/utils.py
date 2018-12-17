#!/usr/bin/env python3

import sys
import time
from grpc._channel import _Rendezvous
from pathlib import Path
from flask import flash
from configparser import ConfigParser
from vectorcloud.models import Command, Output, Status
from vectorcloud import db

try:
    import anki_vector
    from anki_vector.util import degrees, radians
except ImportError:
    sys.exit("Cannot import from anki_vector: Install per Anki instructions")


# establishes routes decorated w/ @public_route as accessible while not signed
# in. See login and register routes for usage
def public_route(decorated_function):
    decorated_function.is_public = True
    return decorated_function


# initiate config parser
config = ConfigParser()


# ------------------------------------------------------------------------------
# Main functions
# ------------------------------------------------------------------------------

# get_stats(): this function gets the results of robot.get_version_state() &
# robot.get_battery_state() and stores it to the status table in the database
# it clears the table at the begining of the function and leaves the data there
# until it is called again.
def get_stats(force=False):
    try:
        status = Status.query.first()
        timestamp = time.time()

        if status is None:
            new_stamp = timestamp - 20
            status = Status(timestamp=new_stamp)
            db.session.add(status)
            db.session.commit()

        elif timestamp - status.timestamp > 15 or force is True:

            # get robot name and ip from config file
            home = Path.home()
            config_file = str(home / ".anki_vector" / "sdk_config.ini")
            f = open(config_file)
            serial = f.readline()
            serial = serial.replace(']', '')
            serial = serial.replace('[', '')
            serial = serial.replace('\n', '')
            f.close()
            config.read(config_file)
            ip = config.get(serial, 'ip')
            name = config.get(serial, 'name')

            # get results from battery state and version state,
            # save to database
            args = anki_vector.util.parse_command_args()
            with anki_vector.Robot(args.serial,
                                   requires_behavior_control=False,
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
                                cube_battery.battery_volts,
                                timestamp=timestamp,
                                ip=ip,
                                name=name)
                db.session.add(status)
                db.session.commit()

        else:
            status.timestamp = timestamp
            db.session.merge(status)
            db.session.commit()

    except _Rendezvous:
        time.sleep(3)
        get_stats(force=True)

    except anki_vector.exceptions.VectorNotFoundException:
        return 'vector_not_found'

    except anki_vector.exceptions.VectorControlTimeoutException:
        return 'vector_stuck'


# robot_do(): this function executes all commands in the command table in order
# with the condition of with anki_vector.Robot(args.serial) as robot:
# if there are commands in the commands in the command table, all you have to
# do to execute is redirect to /execute_commands/ and this function will be
# called. Output is sent to a flash message.
def robot_do(override_output=None):
    robot_commands = Command.query.all()
    try:
        args = anki_vector.util.parse_command_args()
        with anki_vector.Robot(args.serial, enable_camera_feed=True) as robot:

            for command in robot_commands:
                command_string = str(command)
                robot_output_string = str(eval(command_string))
                db_output = Output(output=robot_output_string)
                db.session.add(db_output)
                db.session.commit()

            command_output = Output.query.all()

            if override_output:
                flash(override_output, 'success')

            else:
                for out in command_output:
                    if out is None:
                        pass
                    else:
                        out_string = 'Command completed successfully! Output: \
                            ' + str(out)
                        flash(out_string, 'success')

    except NameError:
        flash('Command not found!', 'warning')

    except anki_vector.exceptions.VectorNotFoundException:
        return 'vector_not_found'

    except anki_vector.exceptions.VectorControlTimeoutException:
        return 'vector_stuck'
    db.session.query(Command).delete()
    db.session.query(Output).delete()
    db.session.commit()
