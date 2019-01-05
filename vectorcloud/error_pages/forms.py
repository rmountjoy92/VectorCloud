#!/usr/bin/env python3

from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class ChangeIP(FlaskForm):

    new_ip = StringField('New IP address', validators=[DataRequired()])

    update = SubmitField('Update')


class ChangeSerial(FlaskForm):

    new_serial = StringField('Serial', validators=[DataRequired()])

    update = SubmitField('Update')
