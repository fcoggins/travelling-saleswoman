import model
import csv

def load_cities(session):

    with open('capitals.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = ",")
        for row in reader:
            city = model.City(city=row[1], state=row[0], lat=row[2], longitude=row[3])
            session.add(city)
    session.commit()

def main(session):

    load_cities(session)


if __name__ == "__main__":
    s= model.connect()
    main(s)