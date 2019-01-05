#!/usr/bin/env python3

import os
from flask import Blueprint, render_template, redirect, url_for, flash
from configparser import ConfigParser
from pathlib import Path
from vectorcloud import db
from vectorcloud.models import Status
from vectorcloud.error_pages.forms import ChangeIP, ChangeSerial

error_pages = Blueprint('error_pages', __name__)

config = ConfigParser()

# ------------------------------------------------------------------------------
# Error Pages
# ------------------------------------------------------------------------------


@error_pages.route("/vector_not_found", methods=['GET', 'POST'])
def vector_not_found():
    form = ChangeIP()
    status = Status.query.first()

    if form.validate_on_submit():
        home = Path.home()
        sdk_config_file = os.path.join(home, '.anki_vector', 'sdk_config.ini')
        f = open(sdk_config_file)
        serial = f.readline()
        serial = serial.replace(']', '')
        serial = serial.replace('[', '')
        serial = serial.replace('\n', '')
        f.close()
        config.read(sdk_config_file)
        config.set(serial, 'ip', form.new_ip.data)

        with open(sdk_config_file, 'w') as configfile:
            config.write(configfile)
            configfile.close()

        flash('IP address updated!', 'success')
        return redirect(url_for('main.home'))
    return render_template('/error_pages/vector_not_found.html',
                           form=form, status=status)


@error_pages.route("/multiple_vectors", methods=['GET', 'POST'])
def multiple_vectors():
    form = ChangeSerial()
    status = Status.query.first()

    if form.validate_on_submit():
        status = Status.query.first()
        if status:
            status.serial = form.new_serial.data
            db.session.merge(status)
            db.session.commit()

        serial = form.new_serial.data
        os.environ["ANKI_ROBOT_SERIAL"] = serial
        flash('Serial updated!', 'success')
        return redirect(url_for('main.home'))
    return render_template('/error_pages/multiple_vectors.html',
                           form=form, status=status)


@error_pages.route("/vector_stuck")
def vector_stuck():
    return render_template('/error_pages/vector_stuck.html')


@error_pages.app_errorhandler(404)
def error_404(error):
    return render_template('/error_pages/404.html'), 404


@error_pages.app_errorhandler(403)
def error_403(error):
    return render_template('/error_pages/403.html'), 403


@error_pages.app_errorhandler(500)
def error_500(error):
    return render_template('/error_pages/500.html'), 500
