#!/usr/bin/env python3

from vectorcloud import app
from vectorcloud.main.utils import database_init
from vectorcloud.manage_vectors.utils import init_vectors

database_init()
init_vectors()


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True, host="0.0.0.0", threaded=True)
