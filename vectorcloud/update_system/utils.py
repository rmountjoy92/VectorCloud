#!/usr/bin/env python3

import platform
import os
import subprocess
from flask import flash
from vectorcloud.application_system.utils import scripts_folder

operating_system = platform.system()
manage_fn = os.path.join(scripts_folder + 'manage_db.py')

if operating_system == 'Windows':
    py_cmd = 'py '

else:
    py_cmd = 'python3 '

migrate_cmd = py_cmd + manage_fn + ' db migrate'
upgrade_cmd = py_cmd + manage_fn + ' db upgrade'


def upgrade_vectorcloud():
    out = subprocess.run('git pull origin master', stdout=subprocess.PIPE,
                         shell=True, encoding='utf-8')

    if out.returncode == 0:
        flash(str(out.stdout), 'success')

    out = subprocess.run(migrate_cmd, stdout=subprocess.PIPE,
                         shell=True, encoding='utf-8')

    if out.returncode == 0:
        flash(str(out.stdout), 'success')

    out = subprocess.run(upgrade_cmd, stdout=subprocess.PIPE,
                         shell=True, encoding='utf-8')

    if out.returncode == 0:
        flash(str(out.stdout), 'success')
