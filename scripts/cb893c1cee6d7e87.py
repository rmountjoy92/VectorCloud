#!/usr/bin/env python3

# Copyright (c) 2018 Anki, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License in the file LICENSE.txt or at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
from database import db, Command, Output, User, Application,\
    AppSupport, Status


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
            print('Saying ' + str(application.script_name) + '...')


if __name__ == "__main__":
    main()
