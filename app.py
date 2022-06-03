#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from email.policy import default
import json
import dateutil.parser 
import babel
from flask import Flask, render_template, request, Response, flash, redirect,jsonify, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy import func
from datetime import date


#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app,db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from models.models import *


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  try:
    data=db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
    records = []
    for entry in data:
      venues=[]
      venues_query=Venue.query.filter_by(city=entry.city,state=entry.state).all()

      for venue in venues_query:
        num_upcoming_shows=0
        for show in venue.shows:
          if show.start_time >= datetime.now():
            num_upcoming_shows +=1

        venues.append({
          "id":venue.id,
          "name":venue.name,
          "num_upcoming_shows":num_upcoming_shows,
        })

      value = {
      "city":  entry.city,
      "state": entry.state,
      "venues": venues
      }
      records.append(value)
  except:
    print(sys.exc_info())
  finally:
    db.session.close()
  
  return render_template('pages/venues.html', areas=records)
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  data=[]
  try:
    search_value="%{0}%".format(request.form.get('search_term', ''))
    venues =Venue.query.filter(Venue.name.ilike(search_value)).all()
    count=0
    for venue in venues:
      count += 1
      num_upcoming_shows=0
      for show in venue.shows:
        if show.start_time >= datetime.now():
          num_upcoming_shows +=1
      data.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": num_upcoming_shows,
      })
    response={
      "count": count,
      "data": data
    }
  except:
    print(sys.exc_info())
  finally:
    db.session.close()

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  venue= Venue.query.get(venue_id)

  past_shows = []
  upcoming_shows =[]

  for show in venue.shows:
    event={
        "artist_id":show.artist_id,
        "artist_name": show.artist.name,
        "artist_image_link":show.artist.image_link,
        "start_time":str(show.start_time)
    }
    if show.start_time < datetime.now():
      past_shows.append(event)
    else:
      upcoming_shows.append(event)

  venue ={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description":venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows) ,
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  
  return render_template('pages/show_venue.html', venue=venue)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  seeking_talent = False
  error = False
  try:
    if "seeking_talent" in request.form:
      seeking_talent=True
    
    venue = Venue(address= request.form["address"], 
                  city = request.form["city"], 
                  facebook_link = request.form["facebook_link"], 
                  genres = request.form.getlist("genres"), 
                  image_link =request.form["image_link"], 
                  name=request.form["name"], 
                  phone= request.form["phone"], 
                  seeking_description= request.form["seeking_description"], 
                  seeking_talent=seeking_talent , 
                  state = request.form["state"], 
                  website_link= request.form["website_link"]
                    )
    db.session.add(venue)
    db.session.commit()

  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      # on unsuccessful db insert, flash an error instead
      flash('An error occurred. Venue ' + request.form["name"] + ' could not be listed.')
       
    else:
       # on successful db insert, flash success
      flash('Venue ' + venue.name + ' was successfully listed!')
    db.session.close()
  return render_template('pages/home.html')
  

 

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  error=False
  try:
    
    Show.query.filter_by(venue_id=venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      # on unsuccessful db insert, flash an error instead
      flash('An error occurred. Venue  could not be deleted.')
    else:
       # on successful db insert, flash success
      flash('Venue  was successfully deleted !')
    db.session.close()
  return jsonify({ 'success': True })


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  try:
    data = db.session.query(Artist.id,Artist.name).order_by('id').all()
  except:
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  data=[]
  try:
    search_value="%{0}%".format(request.form.get('search_term', ''))
    artists =Artist.query.filter(Artist.name.ilike(search_value)).all()
    count=0
    for artist in artists:
      count += 1
      num_upcoming_shows=0
      for show in artist.shows:
        if show.start_time >= datetime.now():
          num_upcoming_shows +=1
      data.append({
        "id": artist.id,
        "name": artist.name,
        "num_upcoming_shows": num_upcoming_shows,
      })
    response={
      "count": count,
      "data": data
    }
  except:
    print(sys.exc_info())
  finally:
    db.session.close()
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  artist= Artist.query.get(artist_id)

  past_shows = []
  upcoming_shows =[]
  upcoming_shows_count=0
  past_shows_count=0


  for show in artist.shows:
    event={
        "venue_id":show.venue_id,
        "venue_name": show.venue.name,
        "venue_image_link":show.venue.image_link,
        "start_time":str(show.start_time)
    }
    if show.start_time < datetime.now():
      past_shows.append(event)
    else:
      upcoming_shows.append(event)

  artist ={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "seeking_description":artist.seeking_description,
    "available_from":artist.available_from,
    "available_to":artist.available_to,
    "upcoming_shows":upcoming_shows,
    "past_shows_count": len(past_shows) ,
    "upcoming_shows_count": len(upcoming_shows),
  }
  
  return render_template('pages/show_artist.html', artist=artist)
   

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id): 
  form = ArtistForm()

  artist= Artist.query.get(artist_id)

  artist={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website_link": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venue,
    "seeking_description":artist.seeking_description,
    "image_link": artist.image_link,
  }
  
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # artist record with ID <artist_id> using the new attributes
  seeking_venue = False
  error = False
 
  try:
    if 'seeking_venue' in request.form:
      seeking_venue= True
    artist= Artist.query.get(artist_id)
    artist.city = request.form["city"]
    artist.facebook_link = request.form["facebook_link"] 
    artist.genres = request.form.getlist("genres")
    artist.image_link =request.form["image_link"]
    artist.name=request.form["name"]
    artist.phone= request.form["phone"]
    artist.seeking_description= request.form["seeking_description"]
    artist.seeking_venue=seeking_venue 
    artist.state = request.form["state"]
    artist.website_link= request.form["website_link"]
          
    db.session.commit()

  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      # on unsuccessful db insert, flash an error instead
      flash('An error occurred. Artist ' + request.form["name"] + ' could not be updated.')
    else:
       # on successful db insert, flash success
      flash('Artist ' + artist.name + ' was successfully updated!')
    db.session.close()


  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue= Venue.query.get(venue_id)
  venue={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address":venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description":venue.seeking_description,
    "image_link": venue.image_link,
  }
  
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  seeking_talent = False
  error = False
 
  try:
    if 'seeking_talent' in request.form:
      seeking_talent= True
    venue= Venue.query.get(venue_id)
    venue.city = request.form["city"]
    venue.facebook_link = request.form["facebook_link"] 
    venue.genres = request.form.getlist("genres")
    venue.image_link =request.form["image_link"]
    venue.name=request.form["name"]
    venue.phone= request.form["phone"]
    venue.seeking_description= request.form["seeking_description"]
    venue.seeking_talent=seeking_talent 
    venue.state = request.form["state"]
    venue.website_link= request.form["website_link"]
          
    db.session.commit()

  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      # on unsuccessful db insert, flash an error instead
      flash('An error occurred. Venue ' + request.form["name"] + ' could not be updated.')
    else:
       # on successful db insert, flash success
      flash('Venue ' + venue.name + ' was successfully updated!')
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  seeking_venue = False
  error = False
 
  try:
    if 'seeking_venue' in request.form:
      seeking_venue= True
    artist = Artist( city = request.form["city"], 
                  facebook_link = request.form["facebook_link"], 
                  genres = request.form.getlist("genres"), 
                  image_link =request.form["image_link"], 
                  name=request.form["name"], 
                  phone= request.form["phone"], 
                  seeking_description= request.form["seeking_description"], 
                  seeking_venue=seeking_venue , 
                  state = request.form["state"], 
                  website_link= request.form["website_link"],
                  available_from= request.form["available_from"],
                  available_to= request.form["available_to"]
                    )
    db.session.add(artist)
    db.session.commit()

  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      # on unsuccessful db insert, flash an error instead
      flash('An error occurred. Artist ' + request.form["name"] + ' could not be listed.')
    else:
       # on successful db insert, flash success
      flash('Artist ' + artist.name + ' was successfully listed!')
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  data=[]
  shows = Show.query.order_by('id').all()
  for show in shows:
    data.append({
      "venue_id": show.venue_id,
      "venue_name":show.venue.name,
      "artist_id": show.artist_id,
      "artist_image_link": str(show.artist.image_link),
      "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  error = False
  try:    
    show = Show(artist_id= request.form["artist_id"], 
                  venue_id = request.form["venue_id"], 
                  start_time = request.form["start_time"], 
                    )
    db.session.add(show)
    db.session.commit()

  except:
    error=True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    if error:
      # on unsuccessful db insert, flash an error instead
      flash('An error occurred. Show could not be listed.')
    else:
       # on successful db insert, flash success
      flash('Show was successfully listed!')
    db.session.close()

  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
