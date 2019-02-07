#!/usr/bin/env python3

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired


class CommandForm(FlaskForm):
    command = StringField('Enter a robot. command',
                          validators=[DataRequired()])

    submit = SubmitField('Stage')


class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])

    by_name = BooleanField('By Name')

    by_description = BooleanField('By Description')

    by_author = BooleanField('By Author')

    go = SubmitField('Search')


class PromptForm(FlaskForm):
    answer = StringField('Input', validators=[DataRequired()])

    send = SubmitField('Send')
