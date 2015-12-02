from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    items = relationship("Item", cascade="all, delete-orphan")

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
               'id': self.id,
               'name': self.name,
               'items': [i.serialize for i in self.items]
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(Text, nullable=False)
    pic_name = Column(String(250))
    category_name = Column(Integer, ForeignKey('category.name'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
               'category_name': self.category_name,
               'description': self.description,
               'title': self.name,
               'id': self.id,
               'user_id': self.user_id
        }


engine = create_engine('sqlite:///catalogwithusers.db')
Base.metadata.create_all(engine)
