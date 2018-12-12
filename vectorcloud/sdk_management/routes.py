#!/usr/bin/env python3

import sys
import platform
from flask import Blueprint, render_template
from vectorcloud.sdk_management.forms import UploadSDK

try:
    import anki_vector
except ImportError:
    sys.exit("Cannot import from anki_vector: Install per Anki instructions")


sdk_management = Blueprint('sdk_management', __name__)


# ------------------------------------------------------------------------------
# sdk management system routes
# ------------------------------------------------------------------------------

operating_system = platform.system()
vectorcloud_sdk_version = "0.5.1"
sdk_version = anki_vector.__version__


# SDK page
@sdk_management.route("/sdk", methods=['GET', 'POST'])
def sdk():
    form = UploadSDK()

    if form.validate_on_submit():
        pass
    return render_template(
        '/settings/sdk.html', title='SDK', form=form, sdk_version=sdk_version)
