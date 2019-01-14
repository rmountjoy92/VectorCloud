#!/usr/bin/env python3

import os
from pathlib import Path


# root path of the application
def get_root_folder():
    curr_folder = os.path.dirname(__file__)
    root_folder = Path(curr_folder).parent
    return root_folder


root_folder = get_root_folder()

vc_folder = os.path.join(root_folder, 'vectorcloud')

lib_folder = os.path.join(root_folder, 'lib')

app_icons_folder = os.path.join(vc_folder, 'static', 'app_icons')

app_store_folder = os.path.join(vc_folder, 'application_store')

packages_folder = os.path.join(app_store_folder, 'packages')

temp_folder = os.path.join(app_store_folder, 'temp')

list_folder = os.path.join(app_store_folder, 'list')

home_folder = Path.home()

sdk_config_file = os.path.join(home_folder, '.anki_vector', 'sdk_config.ini')
