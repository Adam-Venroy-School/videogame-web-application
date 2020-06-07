from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, validators

class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=20)])
    password = PasswordField('Password', [validators.Length(min=8, max=100)])
    register_submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(max=20)])
    password = PasswordField('Password', [validators.Length(max=100)])
    login_submit = SubmitField("Login")
