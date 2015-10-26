from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.types import Date, Float

Base = declarative_base()


class Shelter(Base):
    __tablename__ = 'shelter'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    address = Column(String(250))
    city = Column(String(50))
    state = Column(String(25))
    zipCode = Column(String(5))
    website = Column(String(250))
    maximum_capacity = Column(Integer)
    current_capacity = Column(Integer)


class Puppy(Base):
    __tablename__ = 'puppy'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    date_of_birth = Column(Date)
    breed = Column(String(80))
    gender = Column(String(6), nullable=False)
    weight = Column(Float)
    picture = Column(String(80))
    shelter_id = Column(Integer, ForeignKey('shelter.id'))
    shelter = relationship(Shelter)


engine = create_engine('sqlite:///shelterpuppy.db')


Base.metadata.create_all(engine)
