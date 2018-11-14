#!/usr/bin/env python3

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class CommandForm(FlaskForm):
    command = StringField('Enter a robot. command:',
                          validators=[DataRequired()])

    submit = SubmitField('Stage')


class RegisterForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])

    password = PasswordField('Password:', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Create')


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])

    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Login')
