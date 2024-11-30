import datetime
from flask import render_template, flash, request, redirect, Blueprint, url_for, current_app as app, session, current_app, jsonify, request, make_response
from . import db
from flask_login import login_required, current_user
from .models import Trip, Destination, LikedTrips, Rating
from sqlalchemy import asc, desc
from .forms import CreateTripForm, LoginForm, SignupForm

from .utils import fetch_first_image  # the utility function to get picutres 

#speual python class for the backend for the js 


functions = Blueprint('functions', __name__)


#searching for create 
@functions.route('/search_destinations', methods=['GET'])
@login_required
def search_destinations():
    query = request.args.get('q', '').strip().lower()  # getting the search query from the request
    if not query:
        return jsonify([])  #if not querey return tehge empty list

    #search the database
    results = Destination.query.filter(
        (Destination.name.ilike(f'%{query}%')) |  
        (Destination.country.ilike(f'%{query}%'))  
    ).order_by(Destination.population.desc()).limit(10).all()  #limit results to 10 for performance and ordering by population high to low to avoid ranodm places coming up first 

    data = [{'id': dest.id, 'text': f"{dest.name}, {dest.country}"} for dest in results]
    return jsonify(data)


#searching for places fucntiooon
@functions.route('/search_places', methods=['GET'])
@login_required
def search_places():
    query = request.args.get('q', '').strip().lower()
    country = request.args.get('country', '').strip()

    if not query:
        return jsonify([]) 

    results = Destination.query.filter(
        Destination.name.ilike(f'%{query}%')
    ).order_by(Destination.name.asc()).limit(10).all()

    data = [{'id': dest.id, 'text': f"{dest.name}, {dest.country}"} for dest in results]
    return jsonify(data)


@functions.route('/delete_trip/<int:trip_id>', methods=['DELETE'])
@login_required
def delete_trip(trip_id):
    #query the post
    trip = Trip.query.get_or_404(trip_id)

    # ensure the post belongs to the logged-in user, so no one can just delte it 
    if trip.user_id != current_user.id:
        return jsonify({"success": False, "error": "Unauthorized"}), 403

    try:
        db.session.delete(trip)
        db.session.commit()
        flash(f'successfly deleted {trip.name}')
        return jsonify({"success": True}), 200
    except Exception as e:
        db.session.rollback()
        data = []
        return jsonify({"success": False, "error": str(e)}), 500


@functions.route('/like_trip', methods=['POST'])
@login_required
def like_trip():
    trip_id = request.form.get('trip_id')
    trip = Trip.query.get_or_404(trip_id)

    liked_trip = LikedTrips.query.filter_by(user_id=current_user.id, trip_id=trip_id).first()

    if liked_trip:
        #they can unlinke the trip
        db.session.delete(liked_trip)
        trip.likes = trip.likes - 1 if trip.likes > 0 else 0
    else:
        # like the trip
        new_like = LikedTrips(user_id=current_user.id, trip_id=trip_id)
        db.session.add(new_like)
        trip.likes += 1

    db.session.commit()

    return jsonify({'likes': trip.likes})

@functions.route('/rate/<int:destination_id>', methods=['POST'])
@login_required
def rate_destination(destination_id):
    rating_value = request.form.get('rating')

    #validaiting hte raitng 
    if not rating_value or not rating_value.isdigit():
        return jsonify({'error': 'Invalid rating.'}), 400

    rating_value = int(rating_value)
    if not (1 <= rating_value <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5.'}), 400

    destination = Destination.query.get_or_404(destination_id)

    # user cna only rate on place once, 
    existing_rating = Rating.query.filter_by(user_id=current_user.id, destination_id=destination_id).first()
    if existing_rating:
        #caltulating hte new reating
        old_rating = existing_rating.rating
        existing_rating.rating = rating_value

        #upadting the new rating 
        if destination.ratings_count > 0:
            total_rating = (destination.rating * destination.ratings_count) - old_rating + rating_value
            destination.rating = total_rating / destination.ratings_count
    else:
        #createing a new rating 
        new_rating = Rating(user_id=current_user.id, destination_id=destination_id, rating=rating_value)
        db.session.add(new_rating)

        #updating the rating 
        destination.ratings_count += 1
        if destination.ratings_count > 0:
            total_rating = (destination.rating * (destination.ratings_count - 1)) + rating_value
            destination.rating = total_rating / destination.ratings_count

    #commingitn the chnage4s 
    db.session.commit()

    return jsonify({'message': 'Rating submitted successfully!', 'average_rating': destination.rating}), 200


