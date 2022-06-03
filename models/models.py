from app import db

class Venue(db.Model):
    __tablename__ = 'Venue'
      #TODO: implement any missing fields, as a database migration using Flask-Migrate
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=True)
    city = db.Column(db.String(120),nullable=True)
    state = db.Column(db.String(120),nullable=True)
    address = db.Column(db.String(120),nullable=True)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String),nullable=True)
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean,nullable=True,default=False)
    seeking_description = db.Column(db.String(120))
    shows =  db.relationship('Show',backref='venue',lazy=True)

    def __repr__(self):
      return f'<Venue {self.id} {self.name}>'




class Artist(db.Model):
    __tablename__ = 'Artist'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String,nullable=False)
    city = db.Column(db.String(120),nullable=False)
    state = db.Column(db.String(120),nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String),nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean,nullable=True,default=False)
    seeking_description = db.Column(db.String(120))
    shows = db.relationship('Show',backref='artist',lazy=True)
    available_from = db.Column(db.DateTime(), nullable=True,default="00:00:00")
    available_to = db.Column(db.DateTime(), nullable=True,default="00:00:00")
   

 


    def __repr__(self):
      return f'<Artist {self.id}, {self.name}>'



class Show(db.Model):
  __tablename__='Show'

  id =db.Column(db.Integer, primary_key=True)
  start_time = db.Column(db.DateTime(),nullable=False)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'))
  venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'))