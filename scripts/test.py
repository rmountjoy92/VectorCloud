#!/usr/bin/env python3

import anki_vector
import os
from pathlib import Path
from configparser import ConfigParser

config = ConfigParser()

# serial = os.environ.get('ANKI_ROBOT_SERIAL')
# robot_name = os.environ.get('VECTOR_ROBOT_NAME')
home = Path.home()
config_file = str(home / ".anki_vector" / "sdk_config.ini")
f = open(config_file)
serial = f.readline()
serial = serial.replace(']', '')
serial = serial.replace('[', '')
serial = serial.replace('\n', '')
f.close()
config.read(config_file)
ip = config.get(serial, 'ip')
name = config.get(serial, 'name')
print(ip + '\n' + name)


# args = anki_vector.util.parse_command_args()

# with anki_vector.Robot(args.serial, requires_behavior_control=False,
#                        cache_animation_list=False) as robot:
