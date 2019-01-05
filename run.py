#!/usr/bin/env python3

import os
from vectorcloud import app
from vectorcloud.main.utils import database_init
from vectorcloud.models import Status

database_init()
status = Status.query.first()
if status.serial is not None:
    os.environ["ANKI_ROBOT_SERIAL"] = status.serial

if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, host="0.0.0.0", threaded=True)
