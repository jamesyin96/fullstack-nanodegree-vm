import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.types import Date, Float

Base = declarative_base()


class Shelter(Base):
    __tablename__ = 'Shelter'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    address = Column(String(250), nullable=True)
    city = Column(String(50), nullable=True)
    state = Column(String(2), nullable=True)
    email = Column(String(80), nullable=True)


class Puppy(Base):
    __tablename__ = 'Puppy'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    breed = Column(String(80), nullable=True)
    gender = Column(String(6), nullable=False)
    weight = Column(Float, nullable=True)
    shelter_id = Column(Integer, ForeignKey('Shelter.id'))
    Shelter = relationship(Shelter)


engine = create_engine('sqlite:///shelterpuppy.db')


Base.metadata.create_all(engine)
