import model
import csv

def load_cities(session):

    with open('capitals.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = ",")
        for row in reader:
            city = model.City(city=row[1], state=row[0], lat=row[2], longitude=row[3])
            session.add(city)
    session.commit()

def load_distance(session):
    """loop through all the cities in the cities table and make call to Google Maps
    Distance Matrix API. Then enter the data into the database.
    """
    nodes = model.session.query(model.City).all()
    for i in len(nodes):
        for j in len(nodes):
            print nodes[i].city, nodes[j].city

def main(session):

    load_distance(session)


if __name__ == "__main__":
    s= model.connect()
    main(s)



    # sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper|Distance|
    # distance, expression 'city1_id' failed to locate a name ("name 'city1_id' is not defined"). 
    # If this is a class name, consider adding this relationship() to the 
    # <class 'model.Distance'> class after both dependent classes have been defined.
