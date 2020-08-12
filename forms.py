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
    name = StringField('Name', [validators.Length(min=1, max=100)])
    dev = SelectField('Developer')
    link = StringField('Download Link',[validators.Length(max=200)])
    price = DecimalField('Price',[validators.NumberRange(max=999)])
    image = StringField('Image', [validators.Length(max=9999)])
    desc = StringField('Description', [validators.Length(max=400)])
    video = StringField('Video', [validators.Length(max=100)])
    add_game_submit = SubmitField("Add Game")

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', [validators.Length(max=100)])
    new_password = PasswordField('New Password', [validators.Length(min=8, max=100)])
    password_confirm = PasswordField('Confirm Password',validators=[validators.Length(min=8, max=100), validators.EqualTo('new_password')])
    password_submit = SubmitField("Change Password")
    
class AddDevForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=40)])
    image = StringField('Image', [validators.Length(max=9999)])
    add_dev_submit = SubmitField("Add Developer")
    