from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, DecimalField, SelectField, BooleanField, TextAreaField, validators
from wtforms.widgets import TextArea
from flask_wtf.file import FileField, FileRequired, FileAllowed

class RegisterForm(FlaskForm):
    username = StringField('Username', [validators.Length(min=3, max=20)])
    password = PasswordField('Password', [validators.Length(min=8, max=100)])
    register_submit = SubmitField("Register")

class LoginForm(FlaskForm):
    username = StringField('Username', [validators.Length(max=20)])
    password = PasswordField('Password', [validators.Length(max=100)])
    login_submit = SubmitField("Login")

class AddGameForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=40)])
    dev = SelectField('Developer')
    link = StringField('Download Link',[validators.Length(max=400)])
    price = DecimalField('Price',[validators.NumberRange(max=9999)])
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png'],
                    "Images only")])
    desc = StringField('Description', [validators.Length(max=1000)])
    video = StringField('Video', [validators.Length(max=100)])
    add_game_submit = SubmitField("Add Game")

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', [validators.Length(max=100)])
    new_password = PasswordField('New Password', [validators.Length(min=8, max=100)])
    password_confirm = PasswordField('Confirm Password',validators=[validators.Length(min=8, max=100), 
                                    validators.EqualTo('new_password')])
    password_submit = SubmitField("Change Password")
    
class AddDevForm(FlaskForm):
    name = StringField('Name', [validators.Length(min=1, max=20)])
    image = FileField('Image', validators=[FileRequired(), FileAllowed(['jpg', 'png'], "Images only")])
    add_dev_submit = SubmitField("Add Developer")
    
class ReviewForm(FlaskForm):
    recommend = BooleanField('Recommend')
    review = TextAreaField('Review', validators=[validators.Length(max=1000)], widget=TextArea())
    submit_review = SubmitField("Submit")