from sqlalchemy import create_engine, desc, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Shelter, Puppy
from datetime import timedelta
import datetime

engine = create_engine('sqlite:///shelterpuppy.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

# Query all of the puppies and return the results in
# ascending alphabetical order
puppies = session.query(Puppy).all()
# for puppy in puppies:
#    print puppy.name
#    print puppy.date_of_birth
#    print puppy.gender
#    print puppy.shelter_id

# Query all of the puppies that are less than 6 months old organized
# by the youngest first
current_time = datetime.datetime.utcnow()
six_months_ago = current_time - datetime.timedelta(days=180)
puppies2 = session.query(Puppy).filter(
    Puppy.date_of_birth > six_months_ago
    ).order_by(Puppy.date_of_birth.desc())

# for puppy in puppies2:
#    print puppy.name
#    print puppy.date_of_birth, "\n"

# Query all puppies by ascending weight
puppies3 = session.query(Puppy).order_by(asc(Puppy.weight)).all()

# for puppy in puppies3:
#    print puppy.name
#    print puppy.weight, "\n"

# Query all puppies grouped by the shelter in which they are staying
puppies4 = session.query(Puppy).order_by(Puppy.shelter_id).all()

# for puppy in puppies4:
#    print puppy.name
#    print puppy.shelter_id, "\n"
