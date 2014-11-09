import model, tsp
import csv

def load_cities(session):

    with open('capitals.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = ",")
        for row in reader:
            city = model.City(city=row[1], state=row[0], lat=row[2], longitude=row[3])
            session.add(city)
    session.commit()

def load_distance(session):
    """loop through all the cities in the cities table and calculate the distance
    between them and insert into the matrix.
    """
    nodes = model.session.query(model.City).all()
    for i in range(len(nodes)):
        for j in range(len(nodes)):
            dist = tsp.distance_between_two_cities(nodes[i].lat, nodes[i].longitude,
             nodes[j].lat, nodes[j].longitude)
            distance = model.Distance( city1_id = nodes[i].id, city2_id = nodes[j].id, miles = dist)
            session.add(distance)
    session.commit()

def main(session):

    load_distance(session)


if __name__ == "__main__":
    s= model.connect()
    main(s)



    # sqlalchemy.exc.InvalidRequestError: When initializing mapper Mapper|Distance|
    # distance, expression 'city1_id' failed to locate a name ("name 'city1_id' is not defined"). 
    # If this is a class name, consider adding this relationship() to the 
    # <class 'model.Distance'> class after both dependent classes have been defined.
