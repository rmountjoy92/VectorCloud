#!/usr/bin/env python3

import multiprocessing
import os
import subprocess
from sys import exit
from time import sleep
from flask import render_template, url_for, redirect, Blueprint
from vectorcloud.models import Status
from vectorcloud.main.utils import get_stats
from vectorcloud.main.routes import sdk_version
from vectorcloud.application_system.routes import scripts_folder
from vectorcloud.update_system.utils import upgrade_vectorcloud


update_system = Blueprint('update_system', __name__)


# ------------------------------------------------------------------------------
# Update system routes
# ------------------------------------------------------------------------------

# settings pages
@update_system.route("/update", methods=['GET', 'POST'])
def update():

    err_msg = get_stats()
    if err_msg:
        return redirect(url_for('error_pages.' + err_msg))

    vector_status = Status.query.first()
    return render_template('settings/update.html',
                           vector_status=vector_status,
                           sdk_version=sdk_version)


@update_system.route("/run_upgrade")
def run_upgrade():
    upgrade_vectorcloud()
    return redirect(url_for('update_system.update'))
