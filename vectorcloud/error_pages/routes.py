#!/usr/bin/env python3

from flask import Blueprint, render_template

error_pages = Blueprint('error_pages', __name__)

# ------------------------------------------------------------------------------
# Error Pages
# ------------------------------------------------------------------------------


@error_pages.route("/vector_not_found")
def vector_not_found():
    return render_template('/error_pages/vector_not_found.html')


@error_pages.route("/vector_stuck")
def vector_stuck():
    return render_template('/error_pages/vector_stuck.html')
