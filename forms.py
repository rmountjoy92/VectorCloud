#!/usr/bin/env python3

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class CommandForm(FlaskForm):
    command = StringField('Enter a robot. command:',
                          validators=[DataRequired()])

    submit = SubmitField('Run')
