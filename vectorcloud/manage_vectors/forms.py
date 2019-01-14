#!/usr/bin/env python3

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from vectorcloud.models import User


class AddVector(FlaskForm):
    email = StringField('Anki Account Email', validators=[
        DataRequired(), Length(min=4, max=40)])

    password = PasswordField('Password', validators=[DataRequired()])

    vector_name = StringField('Vector Name e.g. Vector-1234',
                              validators=[DataRequired()])

    vector_serial = StringField('Vector Serial',
                                validators=[DataRequired()])

    vector_ip = StringField('Vector IP',
                            validators=[DataRequired()])

    add = SubmitField('Add')
