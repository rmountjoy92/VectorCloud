#!/usr/bin/env python3

"""
This is an example of how you can interact with VectorCloud's database
from an uploaded application. The package that applications are placed into
contains a module called database that establishes a connection to
VectorCloud's database. In this example we query the application table of
the database to get the application's description, then send the the
description to Vector for him to say.
"""
import anki_vector
import os


# You must import the database instance and models from the databse module
# see database.py for possible imports
from database import Application


def main():

    # Get this file's hex id assigned by VectorCloud (which is the file name)
    application_hex_id = os.path.basename(__file__)
    application_hex_id = application_hex_id.replace('.py', '')

    # here we query the database and get the application's row in the
    # application table
    application = Application.query.filter_by(hex_id=application_hex_id).first()

    args = anki_vector.util.parse_command_args()
    with anki_vector.Robot(args.serial) as robot:

        # if there is a description in our application row, tell Vector to say it
        if application.description:
            robot.say_text(str(application.description))
            print('Saying: ' + str(application.description) + '...')

        # if there is not a description in our application row, tell Vector to let us know
        else:
            robot.say_text("There's no description for " + str(application.script_name))
            print('Saying ' + str(application.description) + '...')


if __name__ == "__main__":
    main()
