#!/usr/bin/env python3

from flask import Flask


app = Flask(__name__)
app.config['SECRET_KEY'] = '66532a62c4048f976e22a39638b6f10e'
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = set(['py'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from vectorcloud import routes
