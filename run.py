#!/usr/bin/env python3

import os
from vectorcloud import app
from vectorcloud.main.utils import database_init
from vectorcloud.manage_vectors.utils import init_vectors
from vectorcloud.paths import temp_folder

database_init()
init_vectors()

temp_exists = os.path.isdir(temp_folder)
if temp_exists is False:
    os.mkdir(temp_folder)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, host="0.0.0.0", threaded=True)
