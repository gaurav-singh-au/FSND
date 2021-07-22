# -*- coding: utf-8 -*-
"""
Created on Thu Jul 22 19:50:04 2021

@author: gsing
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.orm import relationship,backref

db = SQLAlchemy()

def setup_db(app):
    app.config.from_object('config')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gen_user:gen_user@localhost:5432/fyyur'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    migrate = Migrate(app,db)
    db.create_all()
    

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(500))
    seeking_talent = db.Column(db.Boolean)
    shows = relationship("Show")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    def __repr__(self):
        return f"Venue name:{self.name} city: {self.city} state:{self.state}"
# db.create_all()

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    shows = relationship("Show")
    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model):
    __tablename__ = 'Show'
    
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.String(500))
    
def get_past_shows_venue(venue_id,now_time):
    past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < now_time).all()
    return past_shows

def findVenues(term):
    res = db.session.query(Venue).where(Venue.name.ilike(term)).all()
    return res

def findArtists(term):
    res = db.session.query(Artist).where(Artist.name.ilike(term)).all()
    return res

def addShow(t_show):
    db.session.add(t_show)
    db.session.commit()

def addVenue(t_venue):
    db.session.add(t_venue)
    db.session.commit()

def addArtist(t_artist):
    db.session.add(t_artist)
    db.session.commit()

def commit():
    db.session.commit()