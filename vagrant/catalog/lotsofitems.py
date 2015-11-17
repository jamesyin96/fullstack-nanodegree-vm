from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item, User

engine = create_engine('sqlite:///catalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create user1
User1 = User(name="goku", email="goku@gmail.com",
             picture='http://static.comicvine.com/uploads/original/11125/111257581/4862622-goku_by_spongeboss-d35orzj.png')
session.add(User1)
session.commit()

# Create a category1
Category1 = Category(name="Soccer", user_id=1)
session.add(Category1)
session.commit()

# Menu for item1
Item1 = Item(user_id=1, name="British Soccer", category=Category1)
session.add(Item1)
session.commit()

# menu for item2
Item2 = Item(user_id=1, name="American Soccer", category=Category1)
session.add(Item2)
session.commit()


# Create user2
User2 = User(name="vegeta", email="vegeta@gmail.com",
             picture='http://static.comicvine.com/uploads/original/11113/111136107/3959098-1397723110-SSJ_V.png')
session.add(User2)
session.commit()

# Create a category2
Category2 = Category(name="Snowboarding", user_id=2)
session.add(Category2)
session.commit()

# Menu for item1
Item3 = Item(user_id=2, name="Goggles", category=Category2)
session.add(Item3)
session.commit()

# menu for item2
Item4 = Item(user_id=2, name="Snowboard", category=Category2)
session.add(Item4)
session.commit()

print "added menu items!"
