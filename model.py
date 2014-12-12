from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import psycopg2

engine = create_engine("postgresql:///tsp", echo = False)
session = scoped_session(sessionmaker(bind=engine, autocommit = False, autoflush = False))

Base = declarative_base()
Base.query = session.query_property()

### Class declarations
class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key = True)
    city = Column(String(64))
    state = Column(String(64))
    lat = Column(Float(15))
    longitude = Column(Float(15))
    capital = Column(Integer) #0 not a state capital, 1 is a capital
    airport_code = Column(String(3))

class Distance(Base):
    __tablename__ = "distance"

    id = Column(Integer, primary_key = True)
    city1_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    city2_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    miles = Column(Float)
    road_miles = Column(Float)
    polyline = Column(String(10000))
    cost1 = Column(Float, default = None)
    cost2 = Column(Float, default = None)
    cost3 = Column(Float, default = None)
    cost4 = Column(Float, default = None)
    cost5 = Column(Float, default = None)
    cost6 = Column(Float, default = None)
    cost7 = Column(Float, default = None)
    cost8 = Column(Float, default = None)
    cost9 = Column(Float, default = None)
    cost10 = Column(Float, default = None)
    time1 = Column(Float, default = None)
    time2 = Column(Float, default = None)
    time3 = Column(Float, default = None)
    time4 = Column(Float, default = None)
    time5 = Column(Float, default = None)
    time6 = Column(Float, default = None)
    time7 = Column(Float, default = None)
    time8 = Column(Float, default = None)
    time9 = Column(Float, default = None)
    time10 = Column(Float, default = None)

### End class declarations

def connect():
    global ENGINE
    global Session

    ENGINE = create_engine("postgresql:///tsp", echo = True)
    Session = sessionmaker(bind=ENGINE)
    Base.metadata.create_all(ENGINE)

    return Session()

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()