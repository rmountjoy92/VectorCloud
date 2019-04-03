#!/usr/bin/env python3

import os
import signal
from time import sleep
from secrets import token_hex
from sqlalchemy import func
from shutil import copyfile
from flask import render_template, url_for, redirect, flash, request, Blueprint
from vectorcloud.application_system.forms import UploadScript
from vectorcloud.models import Application, AppSupport, Status,\
    ApplicationStore, AppPrompt
from vectorcloud import app, db
from vectorcloud.main.utils import get_stats
from vectorcloud.main.routes import sdk_version
from vectorcloud.application_system.utils import save_icon, save_script,\
    save_script_helpers, run_script_func
from vectorcloud.paths import root_folder, lib_folder
from vectorcloud.application_store.utils import clear_temp_folder


application_system = Blueprint('application_system', __name__)


@application_system.after_request
def add_header(response):
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response
    clear_temp_folder()
    return response


# ------------------------------------------------------------------------------
# Application system routes
# ------------------------------------------------------------------------------
# The upload system works as follows:
# 1. the upload page takes the form data and fills a row in the Application
#    table of the database.
#
# 2. the database columns that are created are:
#    id: unique key, assigned by the database (if it is the first app this = 1)
#    script_name: application's name given to it by the user
#    description: application's description given to it by the user
#    icon: application's icon file name (hex id + '.jpg' or '.png')
#    hex_id: application's hex id assigned to it from vectorcloud
#
# 3. main python file is renamed to (hex id + '.py') and saved to the root path
#
# 4. if added, the icon file is renamed to (hex id + '.jpg' or '.png') and
#    saved to static/app_icons/
#
# 5. if support files added, the upload page takes the form data and fills a
#    row in the AppSupport table of the database. The columns for each support
#    file created are:
#    id: unique key, assigned by the database
#    hex_id: the hex id of the application the file is related to
#    file_name: the file's name e.g. test.py
#
# 6. if added, support files are checked against existing entries and if unique
#    they are added to /lib/


# Upload page
@application_system.route("/upload", methods=['GET', 'POST'])
def upload():
    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    form = UploadScript()
    applications = Application.query.all()

    if form.validate_on_submit():
        if applications:
            for application in applications:
                if application.script_name.lower() == \
                        form.script_name.data.lower():
                    flash('Application named "' + application.script_name +
                          '" already exists, please rename the existing \
                          application and try again.', 'warning')
                    return redirect(url_for('application_system.upload'))

        if form.script.data:
            random_hex = save_script(form.script.data)
            if form.script_helpers.data:
                for helper in form.script_helpers.data:
                    is_in_db = save_script_helpers(helper, random_hex)
                    if is_in_db is True:
                        flash("Helper File Already in Lib!", 'warning')
                        return redirect(url_for('application_system.upload'))

            if form.icon.data:
                icon_fn = save_icon(form.icon.data, random_hex)

            else:
                icon_fn = 'default.png'

            application = Application(hex_id=random_hex,
                                      script_name=form.script_name.data,
                                      description=form.description.data,
                                      icon=icon_fn,
                                      run_in_bkrd=form.run_in_bkrd.data,
                                      author=form.author.data,
                                      website=form.website.data)
            db.session.add(application)
            db.session.commit()
            settings_file = AppSupport(hex_id=application.hex_id,
                                       file_name=application.hex_id + '.ini')
            db.session.add(settings_file)
            db.session.commit()
            settings_file_fn = os.path.join(lib_folder,
                                            application.hex_id + '.ini')
            config_file = open(settings_file_fn, "w+")
            config_file.write('[' + application.script_name + ']\n')
            flash("Application Saved!", 'success')
            return redirect(url_for('main.home'))
        else:
            flash("No script uploaded", 'warning')
        return redirect(url_for('application_system.upload'))
    elif request.method == 'GET':
        form.script_helpers.data = None

    return render_template(
        'applications/upload.html',
        title='Upload',
        form=form,
        vector_status=vector_status,
        sdk_version=sdk_version)


# runs a script from the database by hex id. Hex id is passed into the url
# e.g. /run_script/cb893c1cee6d7e87 would run the script with hex id
# cb893c1cee6d7e87 in the database


@application_system.route("/run_script/<script_hex_id>")
def run_script(script_hex_id):
    application = Application.query.filter_by(hex_id=script_hex_id).first()

    out = run_script_func(script_hex_id)

    prompt = AppPrompt.query.first()
    if prompt:
        pass

    elif out != 'error':
        flash(application.script_name + ' ran succussfully! Output: ' + out,
              'success')

    elif out == 'Process Started!':
        flash(out, 'success')

    else:
        flash('Something is not right. Try again', 'warning')

    return redirect(url_for('main.home'))


@application_system.route("/kill_process/<pid>")
def kill_process(pid):
    application = Application.query.filter_by(pid=pid).first()

    if application:
        application.pid = None
        db.session.commit()

    try:
        os.kill(int(pid), signal.SIGINT)
        flash('Process Killed!', 'success')

    except ProcessLookupError:
        flash('Process has already ended or is not found.', 'warning')

    return redirect(url_for('main.home'))


# this deletes an application by it's unique key (id column). This will delete:
# 1. the main python file
# 2. image file (if not default)
# 3. any added support files associated with the hex id
# 4. database entries for all of the above
@application_system.route("/delete_application/<script_id>",
                          methods=['GET', 'POST'])
def delete_application(script_id):
    application = Application.query.filter_by(id=script_id).first()
    store_app = ApplicationStore.query.filter(func.lower(
        ApplicationStore.script_name) ==
        func.lower(application.script_name)).first()

    if store_app:
        store_app.installed = False
        db.session.merge(store_app)
        db.session.commit()

    hex_id = application.hex_id
    script_fn = application.hex_id + '.py'
    script_path = os.path.join(root_folder, script_fn)
    icon_path = os.path.join(app.root_path,
                             'static/app_icons', application.icon)
    support_files = AppSupport.query.filter_by(hex_id=hex_id)

    for file in support_files:
        file_path = os.path.join(lib_folder, file.file_name)
        os.remove(file_path)
        AppSupport.query.filter_by(id=file.id).delete()

    os.remove(script_path)

    if application.icon != 'default.png':
        os.remove(icon_path)

    Application.query.filter_by(id=script_id).delete()
    db.session.commit()
    flash('Application Deleted!', 'success')
    return redirect(url_for('main.home'))


# this deletes a support file by it's unique key (id column).
# deletes the file from lib and removes databse entry
@application_system.route("/delete_support_file/<int:file_id>",
                          methods=['GET', 'POST'])
def delete_support_file(file_id):
    support_file = AppSupport.query.filter_by(id=file_id).first()
    support_file_path = os.path.\
        join(lib_folder, support_file.file_name)
    os.remove(support_file_path)
    AppSupport.query.filter_by(id=file_id).delete()
    db.session.commit()
    flash(support_file.file_name + ' Deleted!', 'success')
    return redirect(url_for('main.home'))


@application_system.route("/duplicate_application/<script_id>")
def duplicate_application(script_id):
    application = Application.query.filter_by(id=script_id).first()

    script_fn = application.hex_id + '.py'
    config_fn = application.hex_id + '.ini'
    script_path = os.path.join(root_folder, script_fn)
    config_path = os.path.join(lib_folder, config_fn)
    icon_path = os.path.join(app.root_path,
                             'static/app_icons', application.icon)

    new_hex = token_hex(8)
    new_script_fn = new_hex + '.py'
    new_config_fn = new_hex + '.ini'
    new_script_path = os.path.join(root_folder, new_script_fn)
    new_config_path = os.path.join(lib_folder, new_config_fn)
    _, f_ext = os.path.splitext(application.icon)
    new_icon_fn = new_hex + f_ext
    new_icon_path = os.path.join(app.root_path,
                                 'static/app_icons', new_icon_fn)

    copyfile(script_path, new_script_path)
    copyfile(config_path, new_config_path)
    if application.icon != 'default.png':
        copyfile(icon_path, new_icon_path)
    else:
        new_icon_fn = 'default.png'
    application = Application(script_name=new_hex,
                              author=application.author,
                              website=application.website,
                              description=application.description,
                              icon=new_icon_fn,
                              hex_id=new_hex,
                              run_in_bkrd=application.run_in_bkrd)

    app_support = AppSupport(hex_id=new_hex,
                             file_name=new_config_fn)

    db.session.add(application)
    db.session.add(app_support)
    db.session.commit()
    return redirect(url_for('main.home'))
