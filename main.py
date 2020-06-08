from flask import render_template, redirect, url_for, request, flash, Flask
from models import *
from forms import *
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, current_user, login_user, login_required, logout_user

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.urandom(16)

@login_manager.user_loader
def get_user(user_id):
  return User.query.get(int(user_id))

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
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Invalid Username or Password')
    return render_template('login.html', Login_form=Login_form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("home")

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
    elif request.method =='POST' and Register_form.validate_on_submit() == False:
        messages = []       
        if 'username' in Register_form.errors:
            flash("Ensure Username is between 3 and 20 Characters") 
        if 'password' in Register_form.errors:
            flash("Ensure Password is at least 8 characters")
    return render_template('register.html', Register_form=Register_form)

#Redirects pages that dont exist to home
@app.errorhandler(404)
def error(e):
    return redirect('/')

#Redirects Unlogged users to log in page
@app.login_manager.unauthorized_handler
def auth_error():
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)


