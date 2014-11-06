from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine #, DateTime
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker #, scoped_session
# from sqlalchemy import ForeignKey
# from sqlalchemy.orm import relationship, backref

# engine = create_engine("sqlite:///tsp.db", echo = False)
# session = scoped_session(sessionmaker(bind=engine, autocommit = False, autoflush = False))

Base = declarative_base()
# Base.query = session.query_property()
ENGINE = None
Session = None

### Class declarations go here
class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key = True)
    city = Column(String(64))
    state = Column(String(64))
    lat = Column(Float(15))
    longitude = Column(Float(15))


### End class declarations

def connect():
    global ENGINE
    global Session

    ENGINE = create_engine("sqlite:///tsp.db", echo = True)
    Session = sessionmaker(bind=ENGINE)
    Base.metadata.create_all(ENGINE)

    return Session()

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()