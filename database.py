from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os.path

project_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(project_dir,'website.db'))
db = SQLAlchemy(app)

awards = db.Table('awards', db.Column('award_id', db.Integer, db.ForeignKey('award.id'), primary_key=True), db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True))

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False)
    password = db.Column(db.String(40), nullable=False)
    reviews = db.relationship('Review', backref='user', lazy=True)

    def __init__(self, username, password):
        self.username = username
        self.password = password


class Developer(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    logo = db.Column(db.String(40), nullable=True)
    games = db.relationship('Game', backref='developer', lazy=True)


class Game(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    dev = db.Column(db.String, db.ForeignKey('developer.name'), nullable=False)
    link = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float(6), nullable=False)
    desc = db.Column(db.String(1000), nullable=True)
    video = db.Column(db.String(40), nullable=True)
    reviews = db.relationship('Review', backref='game', lazy=True)
    awards = db.relationship('Award', secondary=awards, backref=db.backref('game', lazy=True), lazy='subquery')

class Review(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    reviewer = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    game_name = db.Column(db.String, db.ForeignKey('game.name'), nullable=False)
    review = db.Column(db.String(1000), nullable=False)
    recommend = db.Column(db.Boolean, nullable=True)

class Award(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

db.create_all()
