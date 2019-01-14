#!/usr/bin/env python3

import os
import subprocess
from platform import system as operating_system
from flask import render_template, url_for, redirect, flash, Blueprint
from configparser import ConfigParser
import anki_vector
from vectorcloud.manage_vectors.forms import AddVector
from vectorcloud.models import Vectors, AnkiConf, Status
from vectorcloud.manage_vectors.utils import init_vectors
from vectorcloud.paths import root_folder, sdk_config_file
from vectorcloud.main.utils import get_stats
from vectorcloud.main.routes import sdk_version
from vectorcloud.error_pages.forms import ChangeIP
from vectorcloud import db

manage_vectors = Blueprint('manage_vectors', __name__)


# ------------------------------------------------------------------------------
# manage_vectors routes
# ------------------------------------------------------------------------------
@manage_vectors.route("/manage", methods=['GET', 'POST'])
def manage():
    init_vectors()

    form = AddVector()

    ip_form = ChangeIP()

    vectors = Vectors.query.all()

    for vector in vectors:
        if ip_form.validate_on_submit():
            config = ConfigParser()
            config.read(sdk_config_file)
            config.set(vector.serial, 'ip', ip_form.new_ip.data)

            with open(sdk_config_file, 'w') as configfile:
                config.write(configfile)
                configfile.close()
            flash('IP Address updated!', 'success')
            return redirect(url_for('manage_vectors.manage'))

    if form.validate_on_submit():
        anki_conf = AnkiConf(email=form.email.data,
                             password=form.password.data,
                             serial=form.vector_serial.data,
                             ip=form.vector_ip.data,
                             name=form.vector_name.data)

        db.session.add(anki_conf)
        db.session.commit()

        conf_path = os.path.join(root_folder, 'configure.py')
        if operating_system() == 'Windows':
            py_cmd = 'py '

        else:
            py_cmd = 'python3 '
        cmd = py_cmd + conf_path
        out = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
        flash(str(out.stdout), 'success')
        init_vectors()
        db.session.query(AnkiConf).delete()
        db.session.commit()
        return redirect(url_for('manage_vectors.manage'))

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    return render_template(
        'manage_vectors.html', title='Manage Vectors', form=form,
        vectors=vectors, sdk_version=sdk_version, vector_status=vector_status,
        ip_form=ip_form)


@manage_vectors.route("/set_default_vector/<vector_id>")
def set_default_vector(vector_id):
    curr_def_vector = Vectors.query.filter_by(default=True).first()
    curr_def_vector.default = False
    new_def_vector = Vectors.query.filter_by(id=vector_id).first()
    new_def_vector.default = True
    os.environ["ANKI_ROBOT_SERIAL"] = new_def_vector.serial

    db.session.merge(curr_def_vector)
    db.session.merge(new_def_vector)
    db.session.commit()


@manage_vectors.route("/delete_vector/<vector_id>")
def delete_vector(vector_id):
    vector = Vectors.query.filter_by(id=vector_id).first()

    config = ConfigParser()
    config.read(sdk_config_file)
    config.remove_section(vector.serial)

    with open(sdk_config_file, 'w') as configfile:
        config.write(configfile)
        configfile.close()

    os.remove(vector.cert)

    flash(vector.name + ' deleted!', 'success')
    db.session.query(Vectors).filter_by(id=vector_id).delete()
    db.session.commit()

    return redirect(url_for('manage_vectors.manage'))


@manage_vectors.route("/ping_vector/<vector_id>")
def ping_vector(vector_id):
    vector = Vectors.query.filter_by(id=vector_id).first()

    try:
        with anki_vector.Robot(vector.serial) as robot:
            robot.say_text("Ping")
            flash(vector.name + ' pinged!', 'success')

    except Exception:
        flash(vector.name + ' Not Connected!', 'warning')

    return redirect(url_for('manage_vectors.manage'))
