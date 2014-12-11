
import model, tsp, time, json
import csv
from urllib2 import Request, urlopen
import credentials

def load_flight_data(session):

    api_key = credentials.API_KEY
    url = 'https://www.googleapis.com/qpxExpress/v1/trips/search?key='+api_key
    nodes = model.session.query(model.City).all()
    for i in range (0, 1):
        code1 = nodes[i].airport_code
        city1 = nodes[i].city.replace(" ", "_")
        print city1
        for j in range (52, len(nodes)):
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


def load_directions(session):

    api_key = credentials.API_KEY
    url = 'https://maps.googleapis.com/maps/api/directions/json?'
    nodes = model.session.query(model.City).all()
    for i in range(59, len(nodes)):
        city1 = nodes[i].city
        state1 = nodes[i].state
        city1_escaped = (city1 + "," + state1).replace(" ", "%20")
        city1_underscore = city1.replace (" ", "_")
        for j in range(len(nodes)):
            city2 = nodes[j].city
            state2 = nodes[j].state
            city2_escaped = (city2 + "," + state2).replace(" ", "%20")
            city2_underscore = city2.replace(" ", "_")
            filename = "directions3/"+city1_underscore+'-'+city2_underscore+".json"
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

    #loop through the cities in nodes and extract the city name to grab the file
    for i in range(len(nodes)):
        city1 = nodes[i].city
        airport1 = nodes[i].airport_code
        for j in range(len(nodes)):
            city2 = nodes[j].city
            airport2 = nodes[j].airport_code
            if city1 == city2 or airport1 == airport2:
                continue

            #read road data
            city1_underscore = city1.replace (" ", "_")
            city2_underscore = city2.replace (" ", "_")
            filename = "directions2/"+city1_underscore+'-'+city2_underscore+".json"
            f = open(filename)
            jsondata = f.read()
            data = json.loads(jsondata)
            f.close()
            leg_miles = data["routes"][0]["legs"][0]["distance"]["value"] * 0.000621371
            leg_polyline = data["routes"][0]["overview_polyline"]["points"]

            #read airline data
            filename = "airline_data/"+city1_underscore+'-'+city2_underscore+".json"
            print filename
            f = open(filename)
            jsondata = f.read()
            data = json.loads(jsondata)
            f.close()

            cost = {}
            time = {}
            for k in range(10):
                cost[str(k)]=None
                time[str(k)]=None
            if data['trips'].get('tripOption') == None:
                    print "No Data"
                    distance = model.Distance( city1_id = nodes[i].id, city2_id = nodes[j].id, 
                    road_miles = leg_miles, polyline = leg_polyline, cost1 = cost['0'],cost2 = cost['1'],cost3= cost['2'],
                    cost4= cost['3'],cost5= cost['4'],cost6= cost['5'],cost7= cost['6'],cost8= cost['7'],cost9= cost['8'],cost10=cost['9'], time1=time['0'], time2=time['1'], time3=time['2'],
                    time4=time['3'], time5=time['4'], time6=time['5'], time7=time['6'], time8=time['7'], time9=time['8'], time10=time['9'])
                    session.add(distance)
                    continue
            num_options = len(data['trips']['tripOption'])
            for k in range(num_options):
                option_cost = data['trips']['tripOption'][k]['saleTotal']
                option_time = data['trips']['tripOption'][k]['slice'][0]['duration']
                cost[str(k)]=float(option_cost[3:])
                time[str(k)]=float(option_time)
            print cost['0'], time['0']

            #load everything
            distance = model.Distance( city1_id = nodes[i].id, city2_id = nodes[j].id, 
                road_miles = leg_miles, polyline = leg_polyline, cost1 = cost['0'],cost2 = cost['1'],cost3= cost['2'],
                cost4= cost['3'],cost5= cost['4'],cost6= cost['5'],cost7= cost['6'],cost8= cost['7'],cost9= cost['8'],cost10=cost['9'], time1=time['0'], time2=time['1'], time3=time['2'],
                time4=time['3'], time5=time['4'], time6=time['5'], time7=time['6'], time8=time['7'], time9=time['8'], time10=time['9'])           

            session.add(distance)
    session.commit()



def load_cities(session):

    with open('all_cities.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter = ",")
        for row in reader:
            city = model.City(city=row[1], state=row[0], lat=row[2], longitude=row[3], capital=row[4], airport_code=row[5])
            session.add(city)
    session.commit()

def main(session):

    #read_directions_files(session)
    load_directions(session)
    #load_distance(session)
    #load_cities(session)
    #load_flight_data(session)


if __name__ == "__main__":
    s= model.connect()
    main(s)


