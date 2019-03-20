#!/usr/bin/env python3

import os
from PIL import Image
from shutil import copyfile, make_archive
from zipfile import ZipFile
from secrets import token_hex
from configparser import ConfigParser
from flask import flash, redirect, url_for
from vectorcloud import db
from vectorcloud.models import Application, AppSupport
from vectorcloud.paths import root_folder, lib_folder, packages_folder,\
    temp_folder, app_icons_folder


config = ConfigParser()


# clears all files in /application_store/temp/
def clear_temp_folder():
    file_list = os.listdir(temp_folder)
    for file_name in file_list:
        file_path = os.path.join(temp_folder, file_name)
        os.remove(file_path)


# deletes helper files in case an installation fails
def clear_installed_helpers(hex_id):
    helper_files = AppSupport.query.filter_by(hex_id=hex_id).all()

    for helper in helper_files:
        helper_fn = os.path.join(lib_folder, helper.file_name)
        os.remove(helper_fn)
        db.session.query(AppSupport).\
            filter_by(file_name=helper.file_name).delete()
        db.session.commit()


def install_package(form_package,
                    store_package='False',
                    override_output=False):
    temp_exists = os.path.isdir(temp_folder)

    # find out if application_store/temp/ exists, if not, make it
    if temp_exists is False:
        os.mkdir(temp_folder)

    package_fn = os.path.join(temp_folder, 'temp.zip')
    store_package_fn = os.path.join(packages_folder, store_package)

    if store_package == 'False':
        form_package.save(package_fn)

    else:
        copyfile(store_package_fn, package_fn)

    # extract package to temp folder
    with ZipFile(package_fn, 'r') as zip_ref:
        zip_ref.extractall(temp_folder)

    os.remove(package_fn)

    config_file = os.path.join(temp_folder, 'setup.ini')

    try:
        f = open(config_file)

    except FileNotFoundError:
        flash('There is no setup.ini file in your package, please try again.',
              'warning')
        clear_temp_folder()
        return

    name = f.readline()
    name = name.replace(']', '')
    name = name.replace('[', '')
    name = name.replace('\n', '')
    f.close()
    config.read(config_file)
    script_name = config.get(name, 'script_name')
    applications = Application.query.all()

    # makes sure the new application is unique
    if applications:
        for application in applications:
            if application.script_name.lower() == name.lower():
                clear_temp_folder()
                flash('Application named "' + application.script_name +
                      '" already exists, please rename the existing \
                      application and try again.', 'warning')
                return redirect(url_for('application_store.app_store'))

    helper_string = config.get(name, 'helper_files')

    if helper_string:
        helper_files = helper_string.split()

    else:
        helper_files = []

    icon_file = config.get(name, 'icon_file')
    description = config.get(name, 'description')
    author = config.get(name, 'author')
    website = config.get(name, 'website')
    run_in_bkrd = config.get(name, 'run_in_bkrd')

    if run_in_bkrd.lower() == 'true':
        run_in_bkrd = True

    elif run_in_bkrd.lower() == 'false':
        run_in_bkrd = False

    is_in_db = False
    existing_helpers = []
    random_hex = token_hex(8)

    for helper in helper_files:
        find_helper = AppSupport.query.filter_by(file_name=helper).first()
        if find_helper:
            is_in_db = True
            existing_helpers.append(find_helper.file_name)

    if is_in_db is False:
        for helper in helper_files:
            helper_fn = os.path.join(temp_folder, helper)
            new_helper_fn = os.path.join(lib_folder, helper)

            try:
                os.rename(helper_fn, new_helper_fn)

            except FileNotFoundError:
                flash('Helper file not found, check your setup.ini file',
                      'warning')
                clear_temp_folder()
                return

            appsupport = AppSupport(file_name=helper,
                                    hex_id=random_hex)
            db.session.add(appsupport)
            db.session.commit()

    else:
        for helper in existing_helpers:
            flash(helper + ' already exists in lib.\
                  Please rename your file', 'warning')
        clear_temp_folder()
        return

    script_fn = os.path.join(temp_folder, script_name)
    new_script_fn = os.path.join(root_folder, random_hex + '.py')

    try:
        os.rename(script_fn, new_script_fn)

    except FileNotFoundError:
        flash('Main file not found, check your setup.ini file',
              'warning')
        clear_temp_folder()
        clear_installed_helpers(hex_id=random_hex)
        return

    if icon_file != 'default.png':
        icon_fn = os.path.join(temp_folder, icon_file)
        _, f_ext = os.path.splitext(icon_file)
        hex_icon_name = random_hex + f_ext
        new_icon_fn = os.path.join(app_icons_folder, hex_icon_name)
        output_size = (125, 125)

        try:
            i = Image.open(icon_fn)

        except FileNotFoundError:
            flash('Icon file not found, check your setup.ini file',
                  'warning')
            clear_temp_folder()
            clear_installed_helpers(hex_id=random_hex)
            os.remove(new_script_fn)
            return

        i.thumbnail(output_size)
        i.save(new_icon_fn)
        os.remove(icon_fn)

    else:
        hex_icon_name = 'default.png'

    clear_temp_folder()

    application = Application(script_name=name,
                              author=author,
                              website=website,
                              description=description,
                              icon=hex_icon_name,
                              hex_id=random_hex,
                              run_in_bkrd=run_in_bkrd)
    db.session.add(application)
    db.session.commit()
    helper_files = AppSupport.query.filter_by(hex_id=random_hex).all()
    for helper in helper_files:
        if '.ini' in helper.file_name:
            settings_file_fn = os.path.join(lib_folder, helper.file_name)
            new_settings_file_fn = \
                os.path.join(lib_folder, helper.hex_id + '.ini')
            os.rename(settings_file_fn, new_settings_file_fn)
            helper.file_name = helper.hex_id + '.ini'
            db.session.merge(helper)
            db.session.commit()

    settings_file_fn = os.path.join(lib_folder, random_hex + '.ini')
    if os.path.isfile(settings_file_fn):
        pass
    else:
        settings_file = AppSupport(hex_id=application.hex_id,
                                   file_name=application.hex_id + '.ini')
        db.session.add(settings_file)
        db.session.commit()
        config_file = open(settings_file_fn, "w+")
        config_file.write('[' + application.script_name + ']\n')
    if override_output is False:
        flash('Package Installed!', 'success')


# this creates a zip file that gets downloaded to the users download folder
# first it creates a setup.ini file in application_store/temp and fills it
# in with the metadata from the application's database entry.
# Then it copies all the main python file, any associated helper files, and
# the icon file to the temp folder, then it zips it up returns the zip file's
# path
def export_package(script_id):
    temp_exists = os.path.isdir(temp_folder)

    if temp_exists is False:
        os.mkdir(temp_folder)

    application = Application.query.filter_by(id=script_id).first()
    helper_files = AppSupport.query.filter_by(hex_id=application.hex_id).all()
    helper_list = []

    for helper in helper_files:
        helper_list.append(helper.file_name)

    helper_files_str = ' '.join(helper_list)

    config_file_fn = os.path.join(temp_folder, 'setup.ini')
    config_file = open(config_file_fn, "w+")
    config_file.write('[' + application.script_name + ']\n')
    config_file.write('script_name = ' + application.hex_id + '.py\n')
    config_file.write('helper_files = ' + helper_files_str + '\n')
    config_file.write('icon_file = ' + application.icon + '\n')
    config_file.write('description = ' + application.description + '\n')
    config_file.write('author = ' + application.author + '\n')
    config_file.write('website = ' + application.website + '\n')

    if application.run_in_bkrd is True:
        run_in_bkrd = 'True'

    if application.run_in_bkrd is False:
        run_in_bkrd = 'False'

    config_file.write('run_in_bkrd = ' + run_in_bkrd + '\n')
    config_file.close()

    script_fn = os.path.join(root_folder, application.hex_id + '.py')
    new_script_fn = os.path.join(temp_folder, application.hex_id + '.py')
    copyfile(script_fn, new_script_fn)

    for helper in helper_list:
        helper_fn = os.path.join(lib_folder, helper)
        new_helper_fn = os.path.join(temp_folder, helper)
        copyfile(helper_fn, new_helper_fn)

    if application.icon != 'default.png':
        icon_fn = os.path.join(root_folder, 'vectorcloud',
                               'static', 'app_icons', application.icon)
        new_icon_fn = os.path.join(temp_folder, application.icon)
        copyfile(icon_fn, new_icon_fn)

    zip_name = application.script_name
    zip_name = zip_name.replace(' ', '_')
    make_archive(zip_name, 'zip', temp_folder)
    zip_fn = os.path.join(root_folder, zip_name + '.zip')
    new_zip_fn = os.path.join(temp_folder, zip_name + '.zip')
    os.rename(zip_fn, new_zip_fn)
    return new_zip_fn
