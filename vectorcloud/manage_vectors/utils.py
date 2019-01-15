#!/usr/bin/env python3

import os
from configparser import ConfigParser
from vectorcloud.models import Vectors
from vectorcloud.paths import sdk_config_file
from vectorcloud import db


def init_vectors():
    # Initialize the Vectors table
    db.session.query(Vectors).delete()
    db.session.commit()

    try:
        config = ConfigParser()
        config.read(sdk_config_file)
        vectors = []
        for section in config.sections():
            vectors.append(section)

        for vector in vectors:
            serial = vector
            cert = config.get(vector, 'cert')
            ip = config.get(vector, 'ip')
            name = config.get(vector, 'name')
            guid = config.get(vector, 'guid')
            try:
                default = config.get(vector, 'default')
                if default == 'False':
                    default = False
                else:
                    default = True
            except Exception:
                default = False

            vector_db = Vectors(serial=serial,
                                cert=cert,
                                ip=ip,
                                name=name,
                                guid=guid,
                                default=default)
            db.session.add(vector_db)
            db.session.commit()

        default_vector = Vectors.query.filter_by(default=True).first()
        if default_vector:
            os.environ["ANKI_ROBOT_SERIAL"] = default_vector.serial

    except FileNotFoundError:
        pass
