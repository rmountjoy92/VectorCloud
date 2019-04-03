#!/usr/bin/env python3

import os
import sys
import subprocess
import secrets
from time import sleep
from multiprocessing import Process
from platform import system as operating_system
from vectorcloud import db
from vectorcloud.models import AppSupport, Output, Application
from vectorcloud.main.utils import get_stats
from vectorcloud.paths import root_folder, lib_folder


try:
    from PIL import Image
except ImportError:
    sys.exit("Cannot import from PIL: Do `pip3 install\
             - -user Pillow` to install")


# this function takes the main python file from the form on the upload page,
# generates a hex id, renames the file with the hex id, saves the file to the
# scripts folder, then returns the hex id.
def save_script(form_script):
    random_hex = secrets.token_hex(8)
    file_name = random_hex + '.py'
    script_path = os.path.join(root_folder, file_name)
    form_script.save(script_path)
    return random_hex


# this function takes one of the the support files from the form and the
# application's hex id, figures out if the file already exists in the lib
# package and if it doesn't, it adds the file to the lib package and registers
# it in the database.
def save_script_helpers(helper, random_hex):
    try:
        helper_name = str(helper.filename)
    except AttributeError:
        return

    if len(helper_name) > 1:
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
    icon_path = os.path.join(root_folder, 'vectorcloud',
                             'static/app_icons', file_name)

    output_size = (125, 125)
    i = Image.open(form_icon)
    i.thumbnail(output_size)
    i.save(icon_path)

    return file_name


def start_bkrd_script(py_cmd, script_path, application):
    pid = os.getpid()
    application.pid = pid
    db.session.commit()

    out = subprocess.run(py_cmd + script_path, stdout=subprocess.PIPE,
                         shell=True, encoding='utf-8')

    if out.returncode == 0:
        msg = application.script_name + ' ran succussfully! Output: ' +\
            str(out.stdout)
        output = Output(output=msg)
        db.session.add(output)

    else:
        msg = 'Something is not right, try again.'
        output = Output(output=msg)
        db.session.add(output)

    application.pid = None
    db.session.commit()


def run_script_func(script_hex_id):
    application = Application.query.filter_by(hex_id=script_hex_id).first()
    scriptn = script_hex_id + '.py'
    script_path = os.path.join(root_folder, scriptn)

    if operating_system() == 'Windows':
        py_cmd = 'py '

    else:
        py_cmd = 'python3 '

    if application.run_in_bkrd is False:
        out = subprocess.run(py_cmd + script_path, stdout=subprocess.PIPE,
                             shell=True, encoding='utf-8')

        if out.returncode == 0:
            out = str(out.stdout)

        else:
            out = 'error'

        return out

    else:
        get_stats(force=True)
        t = Process(target=start_bkrd_script,
                    args=(py_cmd, script_path, application))
        t.start()
        out = 'Process Started!'
        sleep(3)
        return out


def set_db_settings(hex_id, settings_file):
    settings_file_fn = os.path.join(lib_folder, hex_id + '.ini')
    f = open(settings_file_fn)
    settings = []

    for line in f.readlines():
        settings.append(line)

    settings_file.settings = ''.join(settings)

    db.session.merge(settings_file)
    db.session.commit()
    return settings_file_fn
