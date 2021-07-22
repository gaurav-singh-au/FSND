#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate

from datetime import datetime as dt

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
from Models import setup_db, Venue,Artist,Show, get_past_shows_venue
from Models import *
setup_db(app)

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
  data = Venue.query.all()
  unique_city_state = set({(v.city,v.state) for v in data})
  all_data = {(c,s):[] for (c,s) in unique_city_state if not c==None and not s==None}
  for v in data:
      if v.state==None or v.city==None: continue
      all_data[(v.city,v.state)].append([v.id,v.name,0])
  json_data = []
  for (c,s),llist in all_data.items():
      dd = {"city":c,"state":s,"venues":[]}
      for ll in llist:
          dd_l = {"id":ll[0],"name":ll[1],"num_upcoming_shows":ll[2]}
          dd["venues"].append(dd_l)
      json_data.append(dd)
  return render_template('pages/venues.html', areas=json_data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  term = request.form.get('search_term', '')
  all_venues = findVenues('%'+term+'%')#select(Venue).where(Venue.name.ilike('%'+term+'%'))# Venue.query.all()
  # print(all_venues)
  response = {"count":len(all_venues), "data":[{"id":aa.id, "name":aa.name, "num_upcoming_shows":len([sh for sh in aa.shows if sh.start_time > dt.now()])} 
                                               for aa in all_venues]}
  # print(response)
  # art_inc = []
  # l_term = [lt.lower() for lt in term.split(" ")]
  # for l_t in l_term:
  #     for aa in all_venues:
  #         if l_t in aa.name.lower() and not aa.id in art_inc:
  #             dd = {"id":aa.id, "name": aa.name, "num_upcoming_shows": 1}
  #             response["count"] += 1
  #             response["data"].append(dd)
  #             art_inc.append(aa.id)
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  this_venue = Venue.query.get(venue_id)
  data_d = {"id":this_venue.id, "name":this_venue.name, 
            "address": this_venue.address, "city":this_venue.city, "state":this_venue.state,
            "facebook_link": this_venue.facebook_link, "image_link": this_venue.image_link,
            "genres": [] if this_venue.genres==None else this_venue.genres.split(";"), "seeking_talent": this_venue.seeking_talent,
            "website": this_venue.website_link, "phone": this_venue.phone,
            "seeking_description": this_venue.seeking_description,
            "past_shows": [], "upcoming_shows":[]}
  # past_shows = [sh for sh in this_venue.shows if sh.start_time < dt.now()]
  past_shows = get_past_shows_venue(venue_id,dt.now())
  upcoming_shows = [sh for sh in this_venue.shows if sh.start_time > dt.now()]
  for sh in past_shows:
      ar = Artist.query.get(sh.artist_id)
      d_show = {
          "artist_id":ar.id,
          "artist_name":ar.name,
          "artist_image_link": ar.image_link,
          "start_time": str(sh.start_time)}
      data_d["past_shows"].append(d_show)
  for sh in upcoming_shows:
      ar = Artist.query.get(sh.artist_id)
      d_show = {
          "artist_id":ar.id,
          "artist_name":ar.name,
          "artist_image_link": ar.image_link,
          "start_time": str(sh.start_time)}
      data_d["upcoming_shows"].append(d_show)
  data_d["past_shows_count"] = len(data_d["past_shows"])
  data_d["upcoming_shows_count"] = len(data_d["upcoming_shows"])
  return render_template('pages/show_venue.html', venue=data_d)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # on successful db insert, flash success
  try:
      vals = request.form
      new_venue = Venue()
      new_venue.name = vals['name']
      new_venue.city = vals['city']
      new_venue.state = vals['state']
      new_venue.address = vals['address']
      new_venue.phone = vals['phone']
      new_venue.genres = ";".join(vals.getlist('genres'))
      new_venue.facebook_link = vals['facebook_link']
      new_venue.image_link = vals['image_link']
      new_venue.website_link = vals['website_link']
      new_venue.seeking_talent = True if 'seeking_talent' in vals else False
      new_venue.seeking_description = vals['seeking_description']
      commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      # db.session.rollback()
  # finally:
  #     db.session.close()
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  try:
      Venue.query.filter(Venue.id==venue_id).delete()
      commit()
      flash('Venue with id ' + venue_id + " was successfully deleted.")
  except:
      flash('An error occur when deleting the Venue with id ' + venue_id)
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  all_artists = Artist.query.all()
  data = []
  for a in all_artists:
      data.append({"id":a.id, "name":a.name})
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  term = request.form.get('search_term', '')
  all_artists = findArtists('%'+term+'%')#select(Venue).where(Venue.name.ilike('%'+term+'%'))# Venue.query.all()
  # print(all_venues)
  response = {"count":len(all_artists), "data":[{"id":aa.id, "name":aa.name, "num_upcoming_shows":len([sh for sh in aa.shows if sh.start_time > dt.now()])} 
                                               for aa in all_artists]}
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  this_artist = Artist.query.get(artist_id)
  data_d = {"id":this_artist.id, "name":this_artist.name, 
            "city":this_artist.city, "state":this_artist.state,
            "facebook_link": this_artist.facebook_link, "image_link": this_artist.image_link,
            "genres": [] if this_artist.genres==None else this_artist.genres.split(";"), "seeking_venue": this_artist.seeking_venue,
            "website": this_artist.website_link, "phone": this_artist.phone,
            "seeking_description": this_artist.seeking_description,
            "past_shows": [], "upcoming_shows":[]}
  shows = this_artist.shows
  now = dt.now()
  for sh in shows:
      vn = Venue.query.get(sh.venue_id)
      d_show = {
          "venue_id":vn.id,
          "venue_name":vn.name,
          "venue_image_link": vn.image_link,
          "start_time": str(sh.start_time)}
      if now < sh.start_time:
          data_d["upcoming_shows"].append(d_show)
      else:
          data_d["past_shows"].append(d_show)
  data_d["past_shows_count"] = len(data_d["past_shows"])
  data_d["upcoming_shows_count"] = len(data_d["upcoming_shows"])
  return render_template('pages/show_artist.html', artist=data_d)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  this_artist = Artist.query.get(artist_id)  
  artist={
    "id": this_artist.id,
    "name": this_artist.name,
    "genres": [] if this_artist.genres==None else this_artist.genres.split(";"),
    "city": this_artist.city,
    "state": this_artist.state,
    "phone": this_artist.phone,
    "website": this_artist.website_link,
    "facebook_link": this_artist.facebook_link,
    "seeking_venue": this_artist.seeking_venue,
    "seeking_description": this_artist.seeking_description,
    "image_link": this_artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  form = ArtistForm(data=artist)
  return render_template('forms/edit_artist.html', form=form, artist=this_artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  this_artist = Artist.query.get(artist_id)
  form = ArtistForm()
  this_artist.name = form.name.data
  this_artist.city = form.city.data
  this_artist.state = form.state.data
  this_artist.phone = form.phone.data
  this_artist.facebook_link = form.facebook_link.data
  this_artist.image_link = form.image_link.data
  this_artist.seeking_venue = form.seeking_venue.data
  this_artist.genres = ";".join(form.genres.data)
  this_artist.seeking_description = form.seeking_description.data
  this_artist.website_link = form.website_link.data
  commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  this_venue = Venue.query.get(venue_id)
  venue={
    "id": this_venue.id,
    "name": this_venue.name,
    "genres": [] if this_venue.genres== None else this_venue.genres.split(";"),
    "address": this_venue.address,
    "city": this_venue.city,
    "state": this_venue.state,
    "phone": this_venue.phone,
    "website": this_venue.website_link,
    "facebook_link": this_venue.facebook_link,
    "seeking_talent": this_venue.seeking_talent,
    "seeking_description": this_venue.seeking_description,
    "image_link": this_venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm(data=venue)
  # form.populate_obj(obj=this_venue)
  # print(dir(form))
  # print(form.validate())
  return render_template('forms/edit_venue.html', form=form, venue=this_venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # venue record with ID <venue_id> using the new attributes
  this_venue = Venue.query.get(venue_id)
  form = VenueForm()
  this_venue.name = form.name.data
  this_venue.address = form.address.data
  this_venue.city = form.city.data
  this_venue.state = form.state.data
  this_venue.phone = form.phone.data
  this_venue.facebook_link = form.facebook_link.data
  this_venue.image_link = form.image_link.data
  this_venue.seeking_talent = form.seeking_talent.data
  this_venue.genres = ";".join(form.genres.data)
  this_venue.seeking_description = form.seeking_description.data
  this_venue.website_link = form.website_link.data
  commit()
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
  try:
      vals = request.form
      print(vals.keys())
      new_artist = Artist()
      new_artist.name = vals['name']
      new_artist.city = vals['city']
      new_artist.state = vals['state']
      # new_artist.address = vals['address']
      new_artist.phone = vals['phone']
      print(dir(vals),vals['genres'],type(vals['genres']), vals.getlist('genres'))
      new_artist.genres = ";".join(vals.getlist('genres'))
      new_artist.facebook_link = vals['facebook_link']
      new_artist.image_link = vals['image_link']
      new_artist.website_link = vals['website_link']
      new_artist.seeking_venue = True if 'seeking_venue' in vals else False
      new_artist.seeking_description = vals['seeking_description']
      # db.session.add(new_artist)
      # db.session.commit()
      addArtist(new_artist)
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      # db.session.rollback()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  all_shows = Show.query.all()
  data = []
  for s in all_shows:
      a = Artist.query.get(s.artist_id)
      v = Venue.query.get(s.venue_id)
      data.append({"venue_id": v.id, "venue_name": v.name, "artist_id": a.id, "artist_name":a.name,
                   "artist_image_link":a.image_link, "start_time": str(s.start_time)})
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
      vals = request.form
      a_id = int(vals["artist_id"])
      v_id = int(vals["venue_id"])
  # on successful db insert, flash success
      all_a_id = [a.id for a in Artist.query.all()]
      all_v_id = [v.id for v in Venue.query.all()]
      # print(all_a_id,all_v_id)
      if not a_id in all_a_id:
          flash(f'Show was not listed as artist id {vals["artist_id"]} was not found!')
      elif not v_id in all_v_id:
          flash(f'Show was not listed as venue id {vals["venue_id"]} was not found!')
      else:
          # db.session.add(Show(venue_id=v_id, artist_id=a_id, start_time=request.form['start_time']))
          addShow(Show(venue_id=v_id, artist_id=a_id, start_time=request.form['start_time']))
          # db.session.commit()
          flash('Show was successfully listed!')
  except:
      flash('Show was not successfully listed!')
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
