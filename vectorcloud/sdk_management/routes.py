#!/usr/bin/env python3

import sys
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

# SDK page
@sdk_management.route("/sdk", methods=['GET', 'POST'])
def sdk():
    sdk_version = anki_vector.__version__
    form = UploadSDK()

    if form.validate_on_submit():
        pass
    return render_template(
        '/settings/sdk.html', title='SDK', form=form, sdk_version=sdk_version)
