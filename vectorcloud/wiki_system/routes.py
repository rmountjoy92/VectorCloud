#!/usr/bin/env python3

from flask import render_template, url_for, redirect, Blueprint, flash
from vectorcloud.models import Status
from vectorcloud.main.utils import get_stats
from vectorcloud.main.routes import sdk_version


wiki_system = Blueprint('wiki_system', __name__)


# ------------------------------------------------------------------------------
# Wiki system routes
# ------------------------------------------------------------------------------

# Wiki pages
@wiki_system.route("/wiki", methods=['GET', 'POST'])
def wiki():

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    return render_template('wiki/wiki_main.html',
                           vector_status=vector_status,
                           sdk_version=sdk_version)


@wiki_system.route("/wiki/applications", methods=['GET', 'POST'])
def applications():

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    return render_template('wiki/applications.html',
                           vector_status=vector_status,
                           sdk_version=sdk_version)


@wiki_system.route("/wiki/api", methods=['GET', 'POST'])
def api():

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    return render_template('wiki/api.html',
                           vector_status=vector_status,
                           sdk_version=sdk_version)


@wiki_system.route("/wiki/database", methods=['GET', 'POST'])
def database():

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    return render_template('wiki/database.html',
                           vector_status=vector_status,
                           sdk_version=sdk_version)


@wiki_system.route("/wiki/tutorials", methods=['GET', 'POST'])
def tutorials():

    err_msg = get_stats()
    if err_msg:
        flash('No Vector is Connected. Error message: ' + err_msg, 'warning')

    vector_status = Status.query.first()
    return render_template('wiki/tutorials.html',
                           vector_status=vector_status,
                           sdk_version=sdk_version)
