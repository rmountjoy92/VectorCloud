#!/usr/bin/env python3

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from vectorcloud.models import User


class CommandForm(FlaskForm):
    command = StringField('Enter a robot. command:',
                          validators=[DataRequired()])

    submit = SubmitField('Stage')


class RegisterForm(FlaskForm):
    username = StringField('Username:', validators=[
                           DataRequired(), Length(min=2, max=20)])

    password = PasswordField('Password:', validators=[DataRequired()])

    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Create')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')


class LoginForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])

    password = PasswordField('Password', validators=[DataRequired()])

    submit = SubmitField('Login')

    remember = BooleanField('Remember Me')
