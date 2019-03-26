#!/usr/bin/env python3

import os
from flask import request
from flask_restful import Resource
from configparser import ConfigParser
from vectorcloud import db
from vectorcloud.models import Status, Command, Application, Vectors
from vectorcloud.main.utils import undock_robot, dock_robot,\
    robot_connect_cube, robot_dock_cube, get_stats,\
    execute_db_commands, server_reboot_func, server_shutdown_func
from vectorcloud.application_system.utils import run_script_func
from vectorcloud.paths import lib_folder


class UndockRobot(Resource):
    def get(self):
        undock_robot()
        return {'Undock': 'Complete'}


class DockRobot(Resource):
    def get(self):
        dock_robot()
        return {'Dock': 'Complete'}


class ConnectCube(Resource):
    def get(self):
        robot_connect_cube()
        return {'Cube': 'Connected'}


class DockCube(Resource):
    def get(self):
        robot_dock_cube()
        return {'Cube': 'Docked'}


class GetStatus(Resource):
    def get(self):
        err_msg = get_stats(force=True)

        if err_msg:
            return err_msg

        status = Status.query.first()
        return {'version': status.version,
                'battery_voltage': status.battery_voltage,
                'battery_level': status.battery_level,
                'status_charging': status.status_charging,
                'cube_battery_level': status.cube_battery_level,
                'cube_id': status.cube_id,
                'cube_battery_volts': status.cube_battery_volts,
                'timestamp': status.timestamp,
                'ip': status.ip,
                'name': status.name,
                'serial': status.serial
                }


class AddCommand(Resource):
    def get(self):
        commands = Command.query.all()

        command_list = []
        for command in commands:
            command_list.append(command.command)

        return {'Commands': command_list}

    def put(self):
        command = request.form['data']
        db_command = Command(command=command)
        db.session.add(db_command)
        db.session.commit()

        commands = Command.query.all()
        command_list = []
        for command in commands:
            command_list.append(command.command)

        return {'Commands': command_list}


class ExecuteCommands(Resource):
    def get(self):
        err_msg = execute_db_commands()
        if err_msg:
            return err_msg
        return {'Commands': 'Complete'}


class ClearCommands(Resource):
    def get(self):
        db.session.query(Command).delete()
        db.session.commit()
        return {'Commands': 'Cleared'}


class RunApplication(Resource):
    def get(self, app_name):
        app_name = app_name.replace('-', ' ')
        application = Application.query.filter_by(script_name=app_name).first()

        if not application:
            output = 'Application not found.'

        else:
            output = run_script_func(application.hex_id)

        return {'Output': output}


class ModRunApplication(Resource):
    def get(self, app_name, options):
        config = ConfigParser()

        app_name = app_name.replace('-', ' ')
        application = Application.query.filter_by(script_name=app_name).first()

        if not application:
            output = 'Application not found.'

        else:
            config_path = os.path.join(lib_folder, application.hex_id + '.ini')
            config.read(config_path)
            num_options = options.count('%')
            options_index = 0
            options_list = []
            for i in range(num_options):
                end = options.find('%', options_index) + 1
                full_option = options[options_index:end]
                equal_sign = full_option.find('=') + 1
                option_name = full_option[0:equal_sign - 1]
                option_value = full_option[equal_sign:]
                option_value = option_value.replace('%', '')
                options_list.append({option_name: option_value})
                options_index = end

            for option in options_list:
                keys = option.keys()
                values = option.values()
                for key in keys:
                    option_name = key
                for value in values:
                    option_value = value
                    option_value = option_value.replace('-', ' ')
                config[application.script_name][option_name] = option_value
                with open(config_path, 'w') as configfile:
                    config.write(configfile)

            output = run_script_func(application.hex_id)

        return {'Output': output}


class ApplicationSettings(Resource):
    def get(self, app_name, options):
        config = ConfigParser()

        app_name = app_name.replace('-', ' ')
        application = Application.query.filter_by(script_name=app_name).first()
        options_list = []
        settings_list = []

        if not application:
            output = 'Application not found.'
            options_list.append(output)

        else:
            config_path = os.path.join(lib_folder, application.hex_id + '.ini')
            config.read(config_path)
            num_options = options.count('%')
            options_index = 0
            for i in range(num_options):
                end = options.find('%', options_index) + 1
                full_option = options[options_index:end]
                equal_sign = full_option.find('=') + 1
                option_name = full_option[0:equal_sign - 1]
                option_value = full_option[equal_sign:]
                option_value = option_value.replace('%', '')
                options_list.append({option_name: option_value})
                options_index = end

            for option in options_list:
                keys = option.keys()
                values = option.values()
                for key in keys:
                    option_name = key
                for value in values:
                    option_value = value
                    option_value = option_value.replace('-', ' ')
                config[application.script_name][option_name] = option_value
                with open(config_path, 'w') as configfile:
                    config.write(configfile)

            config.read(config_path)
            for option in config.options(application.script_name):
                pair = {option: config.get(application.script_name, option)}
                settings_list.append(pair)

        return settings_list


class GetVectors(Resource):
    def get(self):
        vectors = Vectors.query.all()
        vectors_list = []

        if not vectors:
            return 'No Vectors configured!'

        else:
            for vector in vectors:
                vectors_list.append({'serial': vector.serial,
                                     'cert': vector.cert,
                                     'name': vector.name,
                                     'guid': vector.guid,
                                     'default': vector.default
                                     })

        return vectors_list


class ServerShutdown(Resource):
    def get(self):
        server_shutdown_func()
        return {'Server is': 'Shutting down'}


class ServerReboot(Resource):
    def get(self):
        server_reboot_func()
        return {'Server is': 'Rebooting'}
