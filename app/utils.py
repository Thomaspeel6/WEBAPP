
import requests
#https://stackoverflow.com/questions/30595918/is-there-any-api-to-get-image-from-wiki-page

#this class is for the  ulitlies i need, only talks to backend code

def fetch_first_image(destination_name):

    #fetchs the first image URL from a Wikipedia page given a destination name.

    api_url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": destination_name,
        "prop": "pageimages",
        "format": "json",
        "piprop": "original",
    }
    response = requests.get(api_url, params=params)
    data = response.json()

    #extracts the image URL
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "original" in page:
            return page["original"]["source"]
    return None  #return nothing if no image is found

from .models import Trip, Destination, User
from sqlalchemy.orm import joinedload
from datetime import datetime

#follwoing code is my "algorihtm" that sorts the trips based of ur country and contient prefernce 

def get_user_country_continent_preferences(user):
    country_count = {}
    continent_count = {}
    for trip in user.liked_trips:
        for destination in trip.destinations:
            # counrs teh country 
            country = destination.country
            country_count[country] = country_count.get(country, 0) + 1
            #counts continents
            continent = destination.continent
            continent_count[continent] = continent_count.get(continent, 0) + 1
    return country_count, continent_count


#scores each trip in relavance to the user
def score_trip(trip, country_count, continent_count):
    score = 0
    country_weight = 1
    continent_weight = 0.5
    likes_weight = 0.2
    recency_weight = 10
     #gives recenecy the highest eiting os you see new trips more often, adn then the contry weigting 
    for destination in trip.destinations:
        score += country_weight * country_count.get(destination.country, 0)
        score += continent_weight * continent_count.get(destination.continent, 0)
    score += likes_weight * trip.likes

    # receny factor based on posting date
    days_since_posting = max((datetime.utcnow() - trip.created_at).total_seconds() / 86400, 0) # Convert seconds to days
    recency = 1 / (days_since_posting + 1)
    score += recency_weight * recency

    return score

#the personalised trips 
def get_personalised_trips(user):
    #gets the users country/ continet count
    country_count, continent_count = get_user_country_continent_preferences(user)
    # fethes all trips excluding user's own trips
    all_trips = Trip.query.options(joinedload(Trip.destinations)).filter(Trip.user_id != user.id).all()
    trip_scores = []
    #goes thorugh and scores all of them 
    for trip in all_trips:
        score = score_trip(trip, country_count, continent_count)
        trip_scores.append({'trip': trip, 'score': score})
    # all scores are zero, sort by recency, if they have not been active 
    if all(item['score'] == 0 for item in trip_scores):
        trip_scores.sort(key=lambda x: x['trip'].start_date, reverse=True)
    else:
        # sorting the trips by score in descending order
        trip_scores.sort(key=lambda x: x['score'], reverse=True)
  
    return [item['trip'] for item in trip_scores]