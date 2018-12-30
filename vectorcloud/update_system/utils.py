#!/usr/bin/env python3

import platform
import os
import subprocess
from flask import flash
from vectorcloud.application_system.utils import scripts_folder

operating_system = platform.system()
migrate_fn = os.path.join(scripts_folder, 'manage_db.py db migrate')
upgrade_fn = os.path.join(scripts_folder, 'manage_db.py db upgrade')

if operating_system == 'Windows':
    py_cmd = 'py '

else:
    py_cmd = 'python3 '

migrate_cmd = py_cmd + migrate_fn
upgrade_cmd = py_cmd + upgrade_fn


def check_needed():
    out = subprocess.run('git status origin master', stdout=subprocess.PIPE,
                         shell=True, encoding='utf-8')
    if str(out.stdout).find("Your branch is up to date") > -1:
        needed = False
        return needed

    else:
        needed = True
        return needed


def upgrade_vectorcloud():

    out = subprocess.run('git pull origin master', stdout=subprocess.PIPE,
                         shell=True, encoding='utf-8')

    if out.returncode == 0:
        flash(str(out.stdout), 'success')

    out = subprocess.run(migrate_cmd, stderr=subprocess.PIPE,
                         shell=True, encoding='utf-8')

    if out.returncode == 0:
        flash(str(out.stderr), 'success')

    out = subprocess.run(upgrade_cmd, stderr=subprocess.PIPE,
                         shell=True, encoding='utf-8')

    if out.returncode == 0:
        flash(str(out.stderr), 'success')
