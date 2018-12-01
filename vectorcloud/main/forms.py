#!/usr/bin/env python3

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class CommandForm(FlaskForm):
    command = StringField('Enter a robot. command',
                          validators=[DataRequired()])

    submit = SubmitField('Stage')
