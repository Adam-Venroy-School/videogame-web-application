from flask import render_template, redirect, url_for, request
from database import *
from forms import *
import random
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

app.secret_key = 'supersecretkey'

@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
def home():
    return render_template('home.html')

@app.route("/login", methods=['GET', 'POST'])
def login():
    Login_form = LoginForm()
    if request.method == 'POST' and Login_form.validate_on_submit():
        username = Login_form.username.data
        password = Login_form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            print("YES")
        else:
            print("NO")
    return render_template('login.html', Login_form=Login_form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    Register_form = RegisterForm()
    if request.method == 'POST' and Register_form.validate_on_submit():
        name = Register_form.username.data
        password = generate_password_hash(Register_form.password.data,method='sha256',salt_length=8)
        try:
            entry = User(name, password)
            db.session.add(entry)
            db.session.flush()
        except IntegrityError:
            db.session.rollback()
            #Flash Message
        else:
            db.session.commit()
    return render_template('register.html', Register_form=Register_form)


    



#If anything other than home is reached, it will be redirected to home page
@app.errorhandler(404)
def error(e):
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
