#!/usr/bin/env python3

import anki_vector
from vectorcloud.models import Settings, User
from vectorcloud import db


# this makes Vector greet you when you log in from the login page
def login_message():
    try:
        user = db.session.query(User).first()
        settings = db.session.query(Settings).first()
        if settings.greeting_message_enabled is True:

            if settings.custom_greeting_message == 'Default' or 'default':
                robot_msg = 'Hello ' + user.username +\
                    '. Welcome to Vector-Cloud!'

            else:
                robot_msg = settings.custom_greeting_message
            args = anki_vector.util.parse_command_args()
            with anki_vector.Robot(args.serial) as robot:
                robot.behavior.set_eye_color(hue=0.0, saturation=0.0)
                robot.say_text(robot_msg)

    except anki_vector.exceptions.VectorNotFoundException:
        return 'vector_not_found'

    except anki_vector.exceptions.VectorControlTimeoutException:
        return 'vector_stuck'

    except Exception:
        return 'multiple_vectors'
