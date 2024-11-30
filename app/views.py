import datetime
from flask import render_template, flash, request, redirect, Blueprint, url_for, current_app as app, session, current_app, jsonify, request, make_response
from . import db
from flask_login import login_required, current_user
from .models import Trip, Destination, LikedTrips, User
from sqlalchemy import asc, desc
from .forms import CreateTripForm, LoginForm, SignupForm

from .utils import fetch_first_image, get_personalised_trips  

views = Blueprint('views', __name__)

#not logged in homepage
@views.route('/')
def welcome():
    signup_form = SignupForm()
    login_form = LoginForm()  
    current_app.logger.debug(f"current_user: {current_user}, is_authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        return redirect(url_for('views.homepage'))
    return render_template('welcome.html', signup_form=signup_form, login_form=login_form)


#loged in homepafe
@views.route('/homepage')
@login_required
def homepage():
    #displaying the pesronalised trips
    trips = get_personalised_trips(current_user)

    destinations_to_update = []
    for trip in trips:
        for destination in trip.destinations:
            if not destination.image_url:
                #geting the wiki picture 
                destination.image_url = fetch_first_image(destination.name)
                destinations_to_update.append(destination)
    if destinations_to_update:
        db.session.commit()
    return render_template('home.html', trips=trips)

@views.route('/trips/<int:trip_id>')
@login_required
def trip_detail(trip_id):
    #dipslaying hte  trips in detial based off button push 
    trip = Trip.query.get_or_404(trip_id)
    for destination in trip.destinations:
        if not destination.image_url:  
            #gets tje image if they didnt have one alreayd 
            destination.image_url = fetch_first_image(destination.name)
            db.session.add(destination)
            db.session.commit()
    return render_template('trip_detail.html', trip=trip)

@views.route('/destinations/<int:destination_id>')
@login_required
def destination_trips(destination_id):
    #display all trips for a specific destination
    destination = Destination.query.get_or_404(destination_id)
    trips = destination.trips  #acccessing trips using the relationship
    if not destination.image_url:
        destination.image_url = fetch_first_image(destination.name)
        db.session.commit()
    return render_template('destination_trips.html', destination=destination, trips=trips)

@views.route('/destinations', methods=['GET'])
@login_required
def list_continents():
    #distrubting htem all into diffenret continetns 
    continents = db.session.query(Destination.continent).distinct().all()
    return render_template('destinations.html', continents=continents)

@views.route('/countires/<continent>', methods=['GET'])
@login_required
def list_countries(continent):
    #then spliting inot countries 
    countries = db.session.query(Destination.country).filter_by(continent=continent).distinct().all()
    

    # If countries is still an empty list, render template with empty data
    return render_template('countries.html', countries=countries, continent=continent)

@views.route('/places/<country>', methods=['GET'])
@login_required
def list_places(country):
    #split into places withi the country 
    #sort functoin and saerhc and pagnation in this page
    sort_by = request.args.get('sort', 'ranking') 
    query = request.args.get('q', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = 12

    continent_query = db.session.query(Destination.continent).filter_by(country=country).distinct().first()
    continent = continent_query[0] if continent_query else "Unknown"

    # destinations by country
    destinations_query = Destination.query.filter_by(country=country)
    
    # aplying  search filter if there's a query
    if query:
        destinations_query = destinations_query.filter(Destination.name.ilike(f'%{query}%'))

    #PLYING THE  sorting based on the sort parameterr
    if sort_by == 'name':
        destinations_query = destinations_query.order_by(asc(Destination.name))
    elif sort_by == 'name_desc':
        destinations_query = destinations_query.order_by(desc(Destination.name))
    elif sort_by == 'population':
        destinations_query = destinations_query.order_by(asc(Destination.population))
    elif sort_by == 'population_desc':
        destinations_query = destinations_query.order_by(desc(Destination.population))
    elif sort_by == 'trip_count':
        trip_count_subquery = db.session.query(
            trip_destination.destination_id,
            func.count(trip_destination.c.trip_id).label('trip_count')
        ).group_by(trip_destination.c.destination_id).subquery()

        destinations_query = destinations_query.outerjoin(
            trip_count_subquery, Destination.id == trip_count_subquery.c.destination_id
        ).order_by(asc(trip_count_subquery.c.trip_count))
    elif sort_by == 'trip_count_desc':
        trip_count_subquery = db.session.query(
            trip_destination.destination_id,
            func.count(trip_destination.c.trip_id).label('trip_count')
        ).group_by(trip_destination.c.destination_id).subquery()

        destinations_query = destinations_query.outerjoin(
            trip_count_subquery, Destination.id == trip_count_subquery.c.destination_id
        ).order_by(desc(trip_count_subquery.c.trip_count))
    elif sort_by == 'rating':
        destinations_query = destinations_query.order_by(asc(Destination.rating))
    elif sort_by == 'rating_desc':
        destinations_query = destinations_query.order_by(desc(Destination.rating))
    #aplying teh  pagination
    pagination = destinations_query.paginate(page=page, per_page=per_page, error_out=False)


    for destination in pagination.items:
        if not destination.image_url:
            destination.image_url = fetch_first_image(destination.name)
            db.session.commit()
    #checsk if there is an ajax reaquest fromteh seart functions 
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'cards': render_template('cards/card_destination.html', destinations=pagination.items),
            'pagination': render_template('cards/pagination.html', pagination=pagination, query=query, country=country)
        })

    # the response and set the sort parameter as a cookie, this is sot that the sort function is saved over multple pages 
    response = make_response(render_template(
        'places.html',
        destinations=pagination.items,
        pagination=pagination,
        sort_by=sort_by,
        country=country,
        query=query,
        continent=[continent]
    ))
    response.set_cookie(
        'sort', 
        sort_by, 
        samesite='Lax', 
        secure=True     
    )
    return response



@views.route('/create', methods=['GET', 'POST'])
@login_required
def create_trip():
    form = CreateTripForm()
    existing_destinations = Destination.query.all()  # fethcing  all destinations
    if form.validate_on_submit():

        trip = Trip(
            name=form.name.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            user_id=current_user.id,
            description=form.description.data
        )


        # saving the trip to the database
        db.session.add(trip)
        db.session.commit()

        selected_destination_ids = request.form.getlist('destinations[]')
        for dest_id in selected_destination_ids:
            existing_dest = Destination.query.get(int(dest_id))
            if existing_dest:
                trip.destinations.append(existing_dest)

        db.session.commit()     
        flash('Your trip has been created successfully!')
        return redirect(url_for('views.homepage'))

    return render_template('create.html', form=form, existing_destinations= existing_destinations)



@views.route('/profile', methods=['GET'])
@login_required
def profile():
    section = request.args.get('section', 'trips')

    #due ot eht large databse adn that you can like many posts and bisted many destianon, unnless its the section, ie trips dnt laod hte list, laod empty 

    trips = Trip.query.filter_by(user_id=current_user.id).all() if section == 'trips' else []
    liked_trips = current_user.liked_trips if section == 'likes' else []
    visited_destinations = db.session.query(Destination).join(Trip.destinations).filter(Trip.user_id == current_user.id).distinct().all() 
    
    #for the profile stats
    num_visited_destinations = len(visited_destinations)
    visited_countries = {destination.country for destination in visited_destinations}
    num_visited_countries = len(visited_countries)


    for destination in visited_destinations:
        if not destination.image_url:
            #gettin urls for the place if it hasnt alreayd got it 
            destination.image_url = fetch_first_image(destination.name)
            db.session.commit()
    
    user_ratings = {}
    if section == 'destinations':
        # geting the user the user's ratings for each destination
        user_ratings = {
            rating.destination_id: rating.rating for rating in current_user.ratings
        }
    return render_template('profile.html', 
                            trips=trips, 
                            liked_trips=liked_trips,
                            visited_destinations=visited_destinations, 
                            user_ratings=user_ratings,
                            num_visited_destinations=num_visited_destinations,
                            num_visited_countries=num_visited_countries,
                            active_section=section)


#the same funciton as above but as if ur veiwing somoneones profile 
@views.route('/view_profile/<int:user_id>', methods=['GET'])
@login_required
def view_profile(user_id):
    section = request.args.get('section', 'trips')
    viewing_user = User.query.get_or_404(user_id)

    trips = Trip.query.filter_by(user_id=viewing_user.id).all() if section == 'trips' else []
    visited_destinations = db.session.query(Destination).join(Trip.destinations).filter(Trip.user_id == viewing_user.id).distinct().all() 
    num_visited_destinations = len(visited_destinations)
    visited_countries = {destination.country for destination in visited_destinations} 
    num_visited_countries = len(visited_countries)
    for destination in visited_destinations:
        if not destination.image_url:
            destination.image_url = fetch_first_image(destination.name)
            db.session.commit()
    
    user_ratings = {}
    if section == 'destinations':
        user_ratings = {
            rating.destination_id: rating.rating for rating in viewing_user.ratings
        }
    return render_template('viewprofile.html', 
                            trips=trips, 
                            liked_trips=[],
                            visited_destinations=visited_destinations, 
                            user_ratings=user_ratings,
                            num_visited_destinations=num_visited_destinations,
                            num_visited_countries=num_visited_countries,
                            active_section=section,
                            viewing_user=viewing_user)


