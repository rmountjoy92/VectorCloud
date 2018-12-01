#!/usr/bin/env python3

import os
import sys
import secrets
from vectorcloud.models import AppSupport
from vectorcloud import app, db
import scripts

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
