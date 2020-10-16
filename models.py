from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os.path
import os
from flask_login import UserMixin
from sqlalchemy.orm import backref

project_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(project_dir,'website.db'))
db = SQLAlchemy(app)

# Intermediate Table for Games and Users - Acts as User's wishlist
wishlist = (db.Table('wishlist',    
            db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True), 
            db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    reviews = db.relationship('Review', backref='reviews', lazy=True)
    wishlist = db.relationship('Game', secondary=wishlist, backref="user_wishlist", lazy='subquery')
    games_added = db.relationship('Game')
    devs_added = db.relationship('Developer')

    def __init__(self, username, password):
        self.username = username
        self.password = password

class Developer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    logo = db.Column(db.String(40), nullable=True)
    games = db.relationship('Game', cascade='delete', backref=backref('developer', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, name, logo):
        self.name = name
        self.logo = logo

class Game(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False, unique=True)
    dev = db.Column(db.String, db.ForeignKey('developer.name'), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float(6), nullable=False)
    image = db.Column(db.String(200), nullable=True)
    desc = db.Column(db.String(1000), nullable=True)
    video = db.Column(db.String(40), nullable=True)
    reviews = db.relationship('Review', cascade='delete', backref=backref('game', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __init__(self, name, dev, link, price, image, desc, video):
        self.name = name
        self.dev = dev
        self.link = link
        self.price = price
        self.image = image
        self.desc = desc
        self.video = video

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    game_name = db.Column(db.String, db.ForeignKey('game.name'), nullable=False)
    review = db.Column(db.String(1000), nullable=False)
    recommend = db.Column(db.Boolean, nullable=True)

db.create_all()
