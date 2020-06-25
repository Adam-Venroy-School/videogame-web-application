from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DecimalField, SelectField, validators

class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=20)])
    password = PasswordField('Password', [validators.Length(min=8, max=100)])
    register_submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(max=20)])
    password = PasswordField('Password', [validators.Length(max=100)])
    login_submit = SubmitField("Login")

class AddGameForm(FlaskForm):
    name = StringField('Name')
    dev = SelectField('Developer')
    link = StringField('Download Link')
    price = DecimalField('Price')
    image = StringField('Image')
    desc = StringField('Description')
    video = StringField('Video')
    add_game_submit = SubmitField("Add Game")

class AddDevForm(FlaskForm):
    name = StringField('Name')
    image = StringField('Image')
    add_dev_submit = SubmitField("Add Developer")
    