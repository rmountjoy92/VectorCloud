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

            vector_db = Vectors(serial=serial,
                                cert=cert,
                                ip=ip,
                                name=name,
                                guid=guid)
            db.session.add(vector_db)
            db.session.commit()

            default_vector = Vectors.query.filter_by(default=True).first()

            if default_vector is None:
                first_vector = Vectors.query.first()
                first_vector.default = True
                db.session.merge(first_vector)
                db.session.commit()
                default_vector = Vectors.query.filter_by(default=True).first()

            os.environ["ANKI_ROBOT_SERIAL"] = default_vector.serial

    except FileNotFoundError:
        pass
