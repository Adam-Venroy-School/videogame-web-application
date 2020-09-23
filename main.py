from flask import render_template, redirect, url_for, request, flash, Flask, request
from models import *
from forms import *
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, current_user, login_user, login_required, logout_user
from ast import literal_eval

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = os.urandom(16)

# Function for checking if forms are validated - we use this a lot.
def form_validate(form):
    if request.method == 'POST' and form.validate_on_submit():
        return True
    else:
        return False

# Function that returns redirect to page - takes in string that is in form of dict.
def return_page(backpage):
    try:
        # Function that turns string into python dict
        backpage = literal_eval(backpage)
    except SyntaxError:
        # If it does not work for whatever reason, return the user home.
        return redirect(url_for("home"))
    print(list(backpage.keys())[0])
    # Check to see what is in dictionary and redirect depending on content
    if 'user' in backpage:
        page = backpage['user']
        if 'shown_list' in backpage:
            return redirect(url_for('user', username=page,
                                    shown_list=backpage['shown_list']))
        return redirect(url_for("user", username=page))
    elif 'developerlist' in backpage:
        return redirect(url_for("dev_list"))
    elif 'games' in backpage:
        return redirect(url_for('games'))
    elif 'game' in backpage:
        page = backpage['game']
        return redirect(url_for("game", name=page))
    elif 'developer' in backpage:
        page = backpage['developer']
        return redirect(url_for("dev", name=page))
    else:
        return redirect(url_for('games'))

@login_manager.user_loader
def get_user(user_id):
  return User.query.get(int(user_id))

@app.route("/", methods=['GET'])
@app.route("/home", methods=['GET'])
def home():
    return render_template('home.html')

#Login Page - Lets User Login to Website
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    Login_form = LoginForm()
    # Check if form is in post and validated
    if form_validate(Login_form):
        username = Login_form.username.data.strip()
        password = Login_form.password.data
        user = User.query.filter_by(username=username).first()
        # Check if user is true and that password input is equal to password stored in DB
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Invalid Username or Password', 'error')
    return render_template('login.html', Login_form=Login_form)

#Logout - Lets User Log out of Website
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("home")

#Register - Lets User make an account on website
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    Register_form = RegisterForm()
    if form_validate(Register_form):
        print("Test")
        name = Register_form.username.data.strip()
        password = generate_password_hash(Register_form.password.data,method='sha256',
                                        salt_length=8)
        # Attempt to add Username and Password to Database 
        # If it fails due to Unique Constraint, it will return IntegrityError
        try:
            entry = User(name, password)
            db.session.add(entry)
            db.session.flush()
        except IntegrityError:
            #Doesn't add and returns error message 
            db.session.rollback()
            flash("Please enter a unique username", 'error')
        else:
            db.session.commit()
            user = User.query.filter_by(username=name).first()
            login_user(user)
            return redirect(url_for("home"))
            #If Form Validation does not work, return error messages stating why.
    elif request.method =='POST' and Register_form.validate_on_submit() == False:
        if 'username' in Register_form.errors:
            flash("Ensure Username is between 3 and 20 Characters", 'error') 
        if 'password' in Register_form.errors:
            flash("Ensure Password is at least 8 characters", 'error')
    return render_template('register.html', Register_form=Register_form)

# User page - contains info such as wishlist, games user has added, and devs user has added.
@app.route("/user/<username>", methods=['GET', 'POST'])
def user(username):
    if request.args.get('shown_list', None):
        shown_list = request.args.get('shown_list', None)
        print("LIST : {}".format(shown_list))
    else:
        shown_list = None
    #Check to see if User is in DB
    if db.session.query(User.username).filter_by(username=username).scalar() == None:
        print("User not found")
        return redirect(url_for("error_page", error="user_not_found"))

    user = db.session.query(User).filter_by(username=username).one()
    user_page_wishlist = []
    wishlist_games = []
    wishlist_games_id = []
    # Get game ids of the games in the user that we are viewings wishlist
    user_page_wishlist_id = db.session.query(wishlist).filter_by(user_id=user.id).all()
    print(user_page_wishlist_id)
    user_page_wishlist_id = [x[0] for x in user_page_wishlist_id]
    print(user_page_wishlist_id)
    for id in user_page_wishlist_id:
        game = db.session.query(Game).filter_by(id=id).one()
        user_page_wishlist.append(game)
    print('USER WISHLIST:', user_page_wishlist)
        
    # Get game ids of the games in the CURRENT user wishlist.
    if current_user.is_authenticated:    
        wishlist_games_id = db.session.query(wishlist).filter_by(user_id=current_user.id).all()
        wishlist_games_id = [x[0] for x in wishlist_games_id]
        gamelist = Game.query.all()
        for game in gamelist:
            if game.id in wishlist_games_id:
                wishlist_games.append(db.session.query(Game).filter_by(id=game.id).all()[0])

    #Get dev ids of the devs the user has added.
    added_devs = db.session.query(Developer).filter_by(user_id=user.id).all()

    added_games = db.session.query(Game).filter_by(user_id=user.id).all()
    print("ADDED GAMES", added_games)
    print(user.username,"WISHLIST:", user_page_wishlist)
    print("VIEWER WISHLIST:", wishlist_games)
    return render_template("userpage.html", wishlist_games=wishlist_games, 
                        added_games=added_games, user=user, wishlist_games_id=wishlist_games_id, 
                        shown_list=shown_list, user_page_wishlist=user_page_wishlist,
                        added_devs=added_devs)

# Change Password Page - If user wants to change their password, they can.
@app.route("/changepassword", methods=['GET','POST'])
@login_required
def change_password():
    password_form = ChangePasswordForm()
    #Check forms are validated
    if form_validate(password_form):
        print(current_user.password)
        current_password = password_form.current_password.data
        new_password = password_form.new_password.data
        #Check if Password inputted in Current Password is correct
        if check_password_hash(current_user.password, current_password) == False:
            flash("Current Password is wrong")
        else:
            #Set new password to hash
            new_password = generate_password_hash(new_password,method='sha256',salt_length=8)
            #Set user's password to their new password
            current_user.password = new_password
            db.session.commit()
            flash("Password Change Successful", 'success')
    #If validation failed, find out why and flash error.
    elif request.method == 'POST' and password_form.validate_on_submit() == False:
        if password_form.new_password.data != password_form.password_confirm.data:
            flash("Passwords did not match, try again.", 'error')
        else:
            flash("Ensure password is 8 characters.", 'error')
    return render_template("change_password.html", password_form=password_form)

# Add Developer Page - Page where user can add a developer to DB.
@app.route("/adddev", methods=['GET', 'POST'])
@login_required
def add_dev():
    add_dev_form = AddDevForm()
    #Validate Form and if it returns true, add entry to
    if form_validate(add_dev_form):
        print("VALIDATION PASSED")
        dev = add_dev_form.name.data.strip()
        if db.session.query(Developer).filter(func.lower(Developer.name)==dev.lower()).scalar():
            flash("Error: Dev already added")
            return render_template("adddev.html", add_dev_form=add_dev_form)
        if add_dev_form.image.data:
            image = add_dev_form.image.data
            image_name = dev.replace(" ", "") + ".jpg"
            #Save game image in game directory
            image.save(os.path.join(project_dir, "static/images/dev_images", image_name))
            #Change image to source of img
            image = "images/dev_images/" + image_name
            print(image)
        else:
            image = None
        entry = Developer(name=dev, logo=image)
        user = current_user
        try:
            # Add entry to DB and see if it is commitable.
            user.devs_added.append(entry)
            db.session.add(entry)
            db.session.flush()
        except:
            # If flush returns an error, undo changes and flash error.
            db.session.rollback()
            flash('Error: Unable to add Developer', 'error')
        else:
            # If flush returns no error, commit changes and flash success message.
            db.session.commit()
            flash("%s successfully added" % entry.name, 'success')
    # If the user posts and fail validation, return error msgs. 
    elif request.method == 'POST' and add_dev_form.validate_on_submit() == False:  
        if 'name' in add_dev_form.errors:
            flash('Ensure Developer name is under 35 characters.', 'error')
        elif 'image' in add_dev_form.errors:
            flash('Ensure file uploaded is an image', 'error')
    return render_template("adddev.html", add_dev_form=add_dev_form)

# List of Devs
@app.route("/devs", methods=['GET'])
def dev_list():
    #Get all devs in dev table
    devs = db.session.query(Developer).all()
    print(devs)
    return render_template("devlist.html", devs=devs)

# Developer Page - Includes games dev has developed.
@app.route("/devs/<name>", methods=['GET'])
def dev(name):
    wishlist_games = []
    wishlist_games_id = []
    #Check if Developer exists - if false, return to error page
    if db.session.query(Developer.name).filter_by(name=name).scalar() == None:
        print("Dev not found")
        return redirect(url_for("error_page", error="dev_not_found"))
    else:
        developer = db.session.query(Developer).filter_by(name=name).first()
        dev_games = db.session.query(Game).filter_by(dev=developer.name).all()
        print("DEV GAMES:", dev_games)

    #If user is logged in, give option to add/remove to wishlist
    if current_user.is_authenticated:
        wishlist_games = db.session.query(wishlist).filter_by(user_id=current_user.id).all()
        print("WGI:", wishlist_games)
        wishlist_games_id = [x[0] for x in wishlist_games]
        print("WGI", wishlist_games)
        gamelist = Game.query.all()
        #For Loop that searches all games and checks if in user wishlist
    return render_template("dev.html", name=name, developer=developer,
                            dev_games=dev_games, wishlist_games_id=wishlist_games_id)

# Add Game Page - Page where user can add games
@app.route("/addgame", methods=['GET', 'POST'])
@login_required
def add_game():
    add_game_form = AddGameForm()
    # Checks if User came from a dev page - it will display on the page
    if request.args.get('dev_from_page', None):
        dev_from_page = request.args.get('dev_from_page', None)
        print("DEVELOPER : {}".format(dev_from_page))
    else:
        dev_from_page = None
    #Making a list of all devs on the DB that can be selected
    devs = []
    for dev in Developer.query.order_by(Developer.name):
        devs.append((dev.name, dev.logo))
    #Can't add game if there are no devs.
    if len(devs) == 0:
        return redirect(url_for('error_page', error='no_devs'))
    add_game_form.dev.choices = devs
    print(add_game_form.dev.choices)

    if form_validate(add_game_form):
        print("YES")
        game_name = add_game_form.name.data.strip()
        # Check if game name is anything that could break - such as home name
        dev = add_game_form.dev.data
        link = add_game_form.link.data
        price = add_game_form.price.data
        #Check if user uploaded image
        if add_game_form.image.data:
            image = add_game_form.image.data
            image_name = game_name.replace(" ", "") + ".jpg"
            #Save game image in game directory
            image.save(os.path.join(project_dir, "static/images/game_images", image_name))
            #Change image to source of img
            image = "images/game_images/" + image_name
            print(image)
        else:
            image = None
        desc = add_game_form.desc.data
        if add_game_form.video.data:
            video = add_game_form.video.data
            if '=' not in video:
                flash('Video Link does not work.', 'error')
            index = video.find('=') + 1
            video = video[index:]
        else:
            video = None
        entry = Game(game_name, dev, link, price, image, desc, video)
        #Attempt to add entry to database
        try:
            user = db.session.query(User).filter_by(username=current_user.username).first()
            user.games_added.append(entry)
            db.session.add(entry)
            db.session.flush()
        #If integrity error (game_name is already entered) occurs, flash and do not add
        except IntegrityError:
            flash("Game has already been added", 'error')
            db.session.rollback()
            return render_template("addgame.html", add_game_form=add_game_form,
                                    devs=devs, dev_from_page=dev_from_page)
        else:
            flash('%s has been successfully added!' % entry.name, 'success')
            print("GAME ADDED")
            db.session.commit()
    elif request.method == 'POST' and add_game_form.validate_on_submit() == False:
        #If statements checking if an error has occured, and flashing to let user know
        if 'name' in add_game_form.errors:
            flash("Game name needs to be between 1 and 100 characters", 'error') 
        if 'link' in add_game_form.errors:
            flash("Link needs to be less than 400 characters - Please use a link shortner",
            'error')
        if 'price' in add_game_form.errors:
            flash("Price is too high.", 'error')
        if 'description' in add_game_form.errors:
            flash("Description is too long", 'error')
        if 'video' in add_game_form.errors:
            flash("Video Link is too long.", 'error')
        if 'image' in add_game_form.errors:
            flash('Ensure uploaded file is an image.', 'error')
        if 'dev' in add_game_form.errors:
            flash('Please select an Developer.', 'error')
        if len(add_game_form.errors) == 0:
            flash('Unknown Error', 'error')
    print(add_game_form.errors)
    return render_template("addgame.html", add_game_form=add_game_form,
                            devs=devs, dev_from_page=dev_from_page)

# Games list - user can view and add/delete games from wishlist. 
# If they are user that added, they can delete game from DB.
@app.route("/games", methods=['GET'])
def games():
    games=[]
    gamelist = db.session.query(Game).all()
    wishlist_games = []
    #If the User is logged in, check every game to see if on wishlist.
    wishlist_games_id = []
    if current_user.is_authenticated:   # If the user is authenticated, get wishlist
        wishlist_games = db.session.query(wishlist).filter_by(user_id=current_user.id).all()
        print("WG:", wishlist_games)
        wishlist_games_id = [x[0] for x in wishlist_games]
        print("WG:", wishlist_games)
    return render_template('games.html', gamelist=gamelist,
                            wishlist_games_id=wishlist_games_id)

@app.route("/games/<name>", methods=['GET'])
def game(name):
    wishlist_games_id = []
    print(name)
    game = db.session.query(Game).filter_by(name=name).first()
    if game == None:
        return redirect(url_for('error_page', error='no_game_found'))
    print(game)
    if current_user.is_authenticated:
        wishlist_games = db.session.query(wishlist).filter_by(user_id=current_user.id).all()
        wishlist_games_id = [x[0] for x in wishlist_games]

    return render_template('game.html', game=game, wishlist_games_id=wishlist_games_id)

# Function for adding game to wishlist.
@app.route("/wishlist/add/<id>")
@login_required
def add_wishlist(id):
    #Get Game ID
    game = db.session.query(Game).filter_by(id=id).first()
    user = current_user
    backpage = request.args.get('backpage')
    print("BP:", backpage)
    try:
        #Add to user's wishlist the game
        user.wishlist.append(game)
        db.session.flush()
    except:
        #If adding fails, return to error page
        db.session.rollback()
        return redirect(url_for("error_page", error="wishlist"))
    # Checks what page the User came from :
    db.session.commit()
    page = return_page(backpage)
    return page

# Function for deleting game from wishlist.
@app.route("/wishlist/remove/<id>")
@login_required
def remove_wishlist(id):
    user = current_user
    game = db.session.query(Game).filter_by(id=id).first()
    backpage = request.args.get('backpage')
    try:
        user.wishlist.remove(game)
        db.session.flush()
    except:
        db.session.rollback()
        return redirect(url_for("error_page", error="wishlist"))
    db.session.commit()
    # Returns to the page the User came from :
    page = return_page(backpage)
    return page

# Function that deletes game from DB
@app.route("/deletegame/<game>")
@login_required
def delete_game(game):
    backpage = request.args.get('backpage')
    print(backpage)
    user = current_user
    game = db.session.query(Game).filter_by(name=game).first()
    if game == None:
        return redirect(url_for("error_page", error='game_not_found'))
    #Check that user is the one that added game or admin
    if current_user.id == game.user_id or current_user.username == 'admin':
        try:
            db.session.delete(game)
            db.session.flush()
        except:
            #Incase error occurs, User will be returned to error page. No changes to DB
            db.session.rollback()
            return redirect(url_for('error_page', error='delete'))
        else:
            os.remove('static/' + game.image)
            db.session.commit()
        if backpage:
            page = return_page(backpage)
            return page
        else:
            return redirect(url_for('home'))
    else:
        print('FAILED USER CHECK')
        return redirect(url_for('error_page', error='delete'))

# Function that deletes dev from DB
@app.route("/deletedev/<dev>")
@login_required
def delete_dev(dev):
    backpage = request.args.get('backpage')
    user = current_user
    # Get Dev Object user wants to delete
    dev = db.session.query(Developer).filter_by(name=dev).one()
    if dev == None:
        return redirect(url_for("error_page", error='dev_not_found'))
    if current_user.id == dev.user_id or current_user.username == 'admin':
        try:
            db.session.delete(dev)
            db.session.flush()
        except:
            #If errors occur, return error page
            db.session.rollback()
            return redirect(url_for('error_page', error='delete'))
        else:
            os.remove('static/' + dev.logo)
            db.session.commit()
        if backpage:
            page = return_page(backpage)
            return page
        else:
            return redirect(url_for('home'))
    else:
        print('FAILED USER CHECK')
        return redirect(url_for('error_page', error='delete'))

# Erorr page that users will get redirected to if an error occurs.
@app.route("/error", methods=['GET'])
def error_page():
    error = request.args.get('error')
    if error == None:
        return redirect(url_for("home"))
    return render_template("errorpage.html", error=error)
    
#Redirects urls that dont exist to error page
@app.errorhandler(404)
def page_not_found(e):
    return redirect(url_for("error_page", error="404"))

#Redirects Unlogged users to log in page
@app.login_manager.unauthorized_handler
def auth_error():
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)