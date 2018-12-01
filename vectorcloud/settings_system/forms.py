#!/usr/bin/env python3

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class SettingsForms(FlaskForm):
    greeting_message_enabled = BooleanField('Enable Greeting Message')

    custom_greeting_message = StringField('Custom Greeting Message',
                                          validators=[DataRequired()])

    save = SubmitField('Save')
