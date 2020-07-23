from flask import render_template, redirect, url_for, request, flash, Flask, request
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
    if current_user.is_authenticated:
        return redirect(url_for("home"))
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
    if current_user.is_authenticated:
        return redirect(url_for("home"))
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
            flash("Please enter a unique username")
        else:
            db.session.commit()
            user = User.query.filter_by(username=name).first()
            login_user(user)
            return redirect(url_for("home"))
    elif request.method =='POST' and Register_form.validate_on_submit() == False:
        if 'username' in Register_form.errors:
            flash("Ensure Username is between 3 and 20 Characters") 
        if 'password' in Register_form.errors:
            flash("Ensure Password is at least 8 characters")
    return render_template('register.html', Register_form=Register_form)

@app.route("/adddev", methods=['GET', 'POST'])
@login_required
def adddev():
    add_dev_form = AddDevForm()
    if request.method == "POST" and add_dev_form.validate_on_submit():
        dev = add_dev_form.name.data
        image = add_dev_form.image.data
        entry = Developer(name=dev, logo=image)
        db.session.add(entry)
        db.session.commit()
    return render_template("adddev.html", add_dev_form=add_dev_form)

@app.route("/devs", methods=['GET'])
def devlist():
    devs = {}
    for dev in Developer.query.all():
        devs[dev.name] = dev.logo
    print(devs)
    return render_template("devlist.html", devs=devs)

@app.route("/devs/<name>", methods=['GET'])
def dev(name):
    if db.session.query(Developer.name).filter_by(name=name).scalar() == None:
        print("Dev not found")
        return render_template("dev_not_found.html")
    else:
        developer = db.session.query(Developer).filter_by(name=name).first()
        dev_games = db.session.query(Game).filter_by(dev=developer.name).all()
        print(dev_games)
        return render_template("dev.html", name=name, developer=developer, dev_games=dev_games)

@app.route("/addgame", methods=['GET', 'POST'])
@login_required
def addgame():
    add_game_form = AddGameForm()
    if request.args.get('dev_from_page', None):
        dev_from_page = request.args.get('dev_from_page', None)
        print("DEVELOPER : {}".format(dev_from_page))
    else:
        dev_from_page = None
        print(dev_from_page)
    devs = []
    for dev in Developer.query.order_by(Developer.name):
        devs.append((dev.name, dev.logo))
    print(devs)
    if request.method == "POST":
        print("YES")
        game_name = add_game_form.name.data
        dev = add_game_form.dev.data
        link = add_game_form.link.data
        price = add_game_form.price.data
        image = add_game_form.image.data
        desc = add_game_form.desc.data
        video = add_game_form.video.data
        entry = Game(game_name, dev, link, price, image, desc, video)
        db.session.add(entry)
        db.session.commit()
    return render_template("addgame.html", add_game_form=add_game_form, devs=devs, dev_from_page=dev_from_page)

@app.route("/games", methods=['GET'])
def games():
    games=[]
    gamelist = Game.query.all()
    wishlist_games = ['']
    for game in gamelist:
        games.append((game.id, game.name, game.dev, game.image))
    if current_user.is_authenticated:
        wishlist_games = db.session.query(wishlist).filter_by(user_id=current_user.id).all()
        print(wishlist_games)
        wishlist_games = [x[0] for x in wishlist_games]
        print(wishlist_games)
    return render_template('games.html', games=games, wishlist_games=wishlist_games)

@login_required
@app.route("/wishlist/add/<id>")
def add_wishlist(id):
    game = db.session.query(Game).filter_by(id=id).first()
    user = current_user
    backpage = request.args.get('backpage')
    print(game)
    try:
        user.wishlist.append(game)
        db.session.flush()
    except:
        return redirect(url_for("home"))
    db.session.commit()
    if backpage:
        return redirect(url_for(backpage))
    return redirect(url_for('home'))


@login_required
@app.route("/wishlist/remove/<id>")
def remove_wishlist(id):
    user = current_user
    game = db.session.query(Game).filter_by(id=id).first()
    backpage = request.args.get('backpage')
    print(game)
    try:
        user.wishlist.remove(game)
        db.session.flush()
    except:
        return redirect(url_for("home"))
    db.session.commit()
    if backpage:
        return redirect(url_for(backpage))
    return redirect(url_for('home'))
    
#Redirects pages that dont exist to home


#Redirects Unlogged users to log in page
@app.login_manager.unauthorized_handler
def auth_error():
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)


