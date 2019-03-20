#!/usr/bin/env python3

import os
import subprocess
from flask import flash
from platform import system as operating_system
from vectorcloud.paths import root_folder

migrate_fn = os.path.join(root_folder, 'manage_db.py db migrate')
upgrade_fn = os.path.join(root_folder, 'manage_db.py db upgrade')

if operating_system == 'Windows':
    py_cmd = 'py '

else:
    py_cmd = 'python3 '

migrate_cmd = py_cmd + migrate_fn
upgrade_cmd = py_cmd + upgrade_fn


def check_needed():
    subprocess.run('git remote update', shell=True)
    out = subprocess.run('git status -uno', stdout=subprocess.PIPE,
                         shell=True, encoding='utf-8')
    if str(out.stdout).find("Your branch is up to date") > -1:
        needed = False
        return needed

    elif str(out.stdout).find("Your branch is up-to-date") > -1:
        needed = False
        return needed
    else:
        needed = True
        return needed


def upgrade_vectorcloud():

    pull_out = subprocess.run('git pull origin master', stdout=subprocess.PIPE,
                              shell=True, encoding='utf-8')

    if pull_out.returncode == 0:
        # flash(str(out.stdout), 'success')
        pass

    migrate_out = subprocess.run(migrate_cmd, stderr=subprocess.PIPE,
                                 shell=True, encoding='utf-8')

    if migrate_out.returncode == 0:
        # flash(str(out.stderr), 'success')
        pass

    upgrade_out = subprocess.run(upgrade_cmd, stderr=subprocess.PIPE,
                                 shell=True, encoding='utf-8')

    if upgrade_out.returncode == 0:
        # flash(str(out.stderr), 'success')
        pass

    flash("Update Complete. For now it's a good idea to restart the server in \
           the terminal by pressing ctrl+c and rerunning vectorcloud. This \
           will change when we move to a production server.", 'success')
