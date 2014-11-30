
import model, tsp, time, json
import csv
from urllib2 import Request, urlopen
import credentials

def load_flight_data(session):

    api_key = credentials.API_KEY
    url = 'https://www.googleapis.com/qpxExpress/v1/trips/search?key='+api_key
    nodes = model.session.query(model.City).all()
    for i in range (13, len(nodes)):
        code1 = nodes[i].airport_code
        city1 = nodes[i].city.replace(" ", "_")
        print city1
        for j in range (len(nodes)):
            code2 = nodes[j].airport_code
            city2 = nodes[j].city.replace(" ", "_")
            print city2
            if code1 == code2:
                continue
            data = {
              "request": {
                "slice": [
                  {
                    "origin": code1,
                    "destination": code2,
                    "date": "2014-12-15"
                  }
                ],
                "passengers": {
                  "adultCount": 1,
                  "infantInLapCount": 0,
                  "infantInSeatCount": 0,
                  "childCount": 0,
                  "seniorCount": 0
                },
                "solutions": 10,
                "refundable": False
              }
            }

            jsondata=json.dumps(data)
            
            filename = "airline_data/"+city1+'-'+city2+".json"
            req = Request(url, jsondata, {'Content-Type': 'application/json'})
            response = urlopen(req)
            results = response.read()
            f = open(filename, "w")
            f.write(results)
            print filename, "wrote file"
            f.close()






    # data = '{"nw_src": "10.0.0.1/32", "nw_dst": "10.0.0.2/32", "nw_proto": "ICMP", "actions": "ALLOW", "priority": "10"}'
    # req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    # f = urllib2.urlopen(req)
    # for x in f:
    # print(x)
    # f.close()



def load_directions(session):

    api_key = credentials.API_KEY_2
    url = 'https://maps.googleapis.com/maps/api/directions/json?'
    nodes = model.session.query(model.City).all()
    for i in range(1, 59):
        city1 = nodes[i].city
        state1 = nodes[i].state
        city1_escaped = (city1 + "," + state1).replace(" ", "%20")
        city1_underscore = city1.replace (" ", "_")
        for j in range(len(nodes)):
            city2 = nodes[j].city
            state2 = nodes[j].state
            city2_escaped = (city2 + "," + state2).replace(" ", "%20")
            city2_underscore = city2.replace(" ", "_")
            filename = "directions2/"+city1_underscore+'-'+city2_underscore+".json"
            print filename
            parameters = 'origin='+city1_escaped+'&destination='+city2_escaped+'&key='
            request = Request(url + parameters + api_key)
            print url + parameters + api_key
            response = urlopen(request)
            results = response.read() #This gives me back JSON with directions
            print "results"
            f = open(filename, 'w')
            f.write(results)
            print "wrote file"
            f.close()
            time.sleep(1) #so google doesn't get upset

def read_directions_files(session):

    nodes = model.session.query(model.City).all()
    #distance = model.session.query(model.Distance).all()
    #loop through the cities in nodes and extract the city name to grab the file
    for i in range(len(nodes)):
        city1 = nodes[i].city
        airport1 = nodes[i].airport_code
        for j in range(len(nodes)):
            city2 = nodes[j].city
            airport2 = nodes[j].airport_code
            if city1 == city2 or airport1 == airport2:
                continue

            #read road data in
            city1_underscore = city1.replace (" ", "_")
            city2_underscore = city2.replace (" ", "_")
            # filename = "directions2/"+city1_underscore+'-'+city2_underscore+".json"
            # f = open(filename)
            # jsondata = f.read()
            # data = json.loads(jsondata)
            # f.close()
            # leg_miles = data["routes"][0]["legs"][0]["distance"]["value"] * 0.000621371
            # leg_polyline = data["routes"][0]["overview_polyline"]["points"]

            #read airline data in
            filename = "airline_data/"+city1_underscore+'-'+city2_underscore+".json"
            print filename
            f = open(filename)
            jsondata = f.read()
            data = json.loads(jsondata)
            f.close()
            cost = []
            time = []
            for k in range(10):
                if data['trips']['tripOption'][k]['saleTotal']:
                    option_cost = data['trips']['tripOption'][k]['saleTotal']
                    option_time = data['trips']['tripOption'][k]['slice'][0]['duration']
                    cost.append(option_cost)
                    time.append(option_time)
            print cost, time

            #load everything
            # distance = model.Distance( city1_id = nodes[i].id, city2_id = nodes[j].id, 
            #     road_miles = leg_miles, polyline = leg_polyline, cost1,cost2,cost3,
            #     cost4,cost5,cost6,cost7,cost8,cost9,cost10 = *cost, time1, time2, time3,
            #     time4, time5, time6, time7, time8, time9, time10 = *time)
            

            

            # session.add(distance)
    # session.commit()



def load_cities(session):

    with open('all_cities.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = ",")
        for row in reader:
            city = model.City(city=row[1], state=row[0], lat=row[2], longitude=row[3], capital=row[4], airport_code=row[5])
            session.add(city)
    session.commit()

# def load_distance(session):
#     """loop through all the cities in the cities table and calculate the distance
#     between them and insert into the matrix.
#     """
#     nodes = model.session.query(model.City).all()
#     for i in range(len(nodes)):
#         for j in range(i+1, len(nodes)):
#             dist = tsp.distance_between_two_cities(nodes[i].lat, nodes[i].longitude,
#              nodes[j].lat, nodes[j].longitude)
#             # dist_object = model.Distance.query.filter_by(model.Distance.city1_id=i, model.Distance.city2_id=j).one()
#             dist_object = model.session.query(model.Distance).filter_by(city1_id=i,city2_id=j).first()
#             if dist_object:
#                 print "i is", i
#                 print "j is", j
#                 dist_object.miles = dist
#                 print dist_object.miles
#                 session.add(dist_object)
#     session.commit()
#     session.close()

def main(session):

    #read_directions_files(session)
    #load_directions(session)
    #load_distance(session)
    #load_cities(session)
    load_flight_data(session)


if __name__ == "__main__":
    s= model.connect()
    main(s)


