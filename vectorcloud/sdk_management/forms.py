#!/usr/bin/env python3

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField


class UploadSDK(FlaskForm):
    sdk_file = FileField('Upload SDK .zip file',
                         validators=[FileAllowed(['py'])])

    install = SubmitField('Install')
