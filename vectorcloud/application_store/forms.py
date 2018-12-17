#!/usr/bin/env python3

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired


class UploadPackage(FlaskForm):

    package = FileField('Install package', validators=[FileAllowed(['zip'])])

    install = SubmitField('Install')


class AdminAdd(FlaskForm):
    script_name = StringField('Name of SDK application',
                              validators=[DataRequired()])

    description = TextAreaField('Description')

    author = StringField('Author Name')

    website = StringField('Website')

    icon = StringField('Icon Name')

    zip_file = StringField('Zip File Name')

    add = SubmitField('Add')

    update = SubmitField('Update')
