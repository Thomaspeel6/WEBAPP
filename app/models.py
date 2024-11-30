from . import db
from flask_login import UserMixin
from sqlalchemy import Index, UniqueConstraint
from datetime import datetime

class User( UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True)
    name= db.Column(db.String(100))
    password = db.Column(db.String(100))
    trips = db.relationship('Trip', backref='user', lazy=True)
    liked_trips = db.relationship('Trip', secondary='liked_trips', backref='liked_by_users', lazy=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    destinations = db.relationship('Destination', secondary='trip_destination', backref='trips', lazy=True)
    likes = db.Column(db.Integer, default=0, server_default='0')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow) 

class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    country = db.Column(db.String(100), nullable=False, index=True)
    continent = db.Column(db.String(100), nullable=False)
    population = db.Column(db.Integer)
    image_url = db.Column(db.String(255))
    rating = db.Column(db.Float, default=0, server_default='0')  
    ratings_count = db.Column(db.Integer, default=0, server_default='0') 
    ratings = db.relationship('Rating', backref='destination', lazy=True)  
class LikedTrips(db.Model):
    __tablename__ = 'liked_trips'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trip_id = db.Column(db.Integer, db.ForeignKey('trip.id'))
    __table_args__ = (
        UniqueConstraint('user_id', 'trip_id', name='unique_user_trip'),
    )
class Rating(db.Model):
    __tablename__ = 'rating'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  
    destination_id = db.Column(db.Integer, db.ForeignKey('destination.id'), nullable=False)  
    rating = db.Column(db.Integer, nullable=False)  
    __table_args__ = (
        UniqueConstraint('user_id', 'destination_id', name='unique_user_destination_rating'),
    )
trip_destination = db.Table('trip_destination',
    db.Column('trip_id', db.Integer, db.ForeignKey('trip.id'), primary_key=True),
    db.Column('destination_id', db.Integer, db.ForeignKey('destination.id'), primary_key=True)
)