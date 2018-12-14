#!/usr/bin/env python3


# VectorCloud database integration example

import os
import anki_vector

# import the Application database model
from vectorcloud.models import Application


# get this application's hex id and query the database for its entry
curr_file = os.path.basename(__file__)
curr_file = curr_file.replace('.py', '')
application = Application.query.filter_by(hex_id=curr_file).first()

# set the message we'll send to Vector as the application's description
robot_msg = application.description


def main():
    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:
        if robot_msg:
            print("Saying: " + robot_msg)
            robot.say_text(robot_msg)
        else:
            robot.say_text('There is no description for ' +
                           application.script_name)


if __name__ == "__main__":
    main()
