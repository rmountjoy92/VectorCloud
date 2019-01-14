#!/usr/bin/env python3

from flask import render_template, url_for, redirect, Blueprint, flash
from vectorcloud.models import Status
from vectorcloud.main.utils import get_stats
from vectorcloud.main.routes import sdk_version
from vectorcloud.version import vectorcloud_version
from vectorcloud.update_system.utils import upgrade_vectorcloud, check_needed


update_system = Blueprint('update_system', __name__)


# ------------------------------------------------------------------------------
# Update system routes
# ------------------------------------------------------------------------------

# settings pages
@update_system.route("/update", methods=['GET', 'POST'])
def update():
    needed = check_needed()

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    return render_template('settings/update.html',
                           vector_status=vector_status,
                           sdk_version=sdk_version,
                           needed=needed,
                           vectorcloud_version=vectorcloud_version)


@update_system.route("/run_upgrade")
def run_upgrade():
    upgrade_vectorcloud()
    return redirect(url_for('update_system.update'))
