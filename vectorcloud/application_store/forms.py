#!/usr/bin/env python3

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField


class UploadPackage(FlaskForm):

    package = FileField('Install package', validators=[FileAllowed(['zip'])])

    install = SubmitField('Install')
