from flask import Flask, render_template, url_for

from flask_wtf.file import FileField, FileAllowed
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.numeric import IntegerField
from wtforms.fields.simple import FileField
from wtforms.validators import InputRequired, Length, NumberRange, ValidationError

from app import *


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    name = StringField(validators=[InputRequired(), Length(
        min=1, max=20)], render_kw={"placeholder": "Name"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')
    def validate_username(self, username):
        existing_username = User.query.filter_by(
            username=username.data).first()
        if existing_username:
            raise ValidationError(
                'That username already exists, please choose a different one.')

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(
        min=4, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

class EditProfilePicture(FlaskForm):
    profilePicture = FileField("Change Picture", validators=[FileAllowed(['jpg', 'png'])])
    profileSubmit = SubmitField('Change Picture')

class AddIcon(FlaskForm):
    iconPicture = FileField("Change Picture", validators=[InputRequired(), FileAllowed(['png', 'jpg'])])
    name = StringField(validators=[InputRequired(), Length(
        min=1, max=20)], render_kw={"placeholder": "Name"})
    website = StringField(validators=[InputRequired(), Length(
        min=1, max=20)], render_kw={"placeholder": "URL"})
    height = IntegerField(validators=[InputRequired(), NumberRange(
        min=20, max=500)], render_kw={"placeholder": "Height"})
    width = IntegerField(validators=[InputRequired(), NumberRange(
        min=20, max=500)], render_kw={"placeholder": "Width"})
    loadOrder = IntegerField(validators=[InputRequired(), NumberRange(
        min=1, max=20)], render_kw={"placeholder": "Order"})
    iconSubmit = SubmitField('Create Icon')