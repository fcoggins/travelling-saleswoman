from flask import Flask, request, session as fsksession, render_template, g, redirect, url_for, flash
import os, jinja2, random, string, json, sys
import tsp, model, time, shelve
#import credentials

app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY", '\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03')
app.jinja_env.undefined = jinja2.StrictUndefined

polyline_dict = {}

@app.route("/")
def index():
    """Return the index page. Get data and build a polyline dictionary. 
    Key will be edge in the form "city1_id-city2_id" and value will be 
    the polyline."""
    
    global polyline_dict

    if not os.path.isfile("polyline_ref.db"):
        polyline_dict = shelve.open("polyline_ref")
        build_file();
    else:
        polyline_dict = shelve.open("polyline_ref")


    return render_template("index.html")


def build_file():

    global polyline_dict
    distance = model.session.query(model.Distance).all()
    time1 = time.time()
    for i in range(len(distance)):
        for j in range(len(distance)):
            key = str(distance[i].city1_id)+"-"+str(distance[i].city2_id)
            value = distance[i].polyline
            polyline_dict[key]=value
    time2 = time.time()
    # print "Cost to build table", (time2-time1)


@app.route("/get_initial_data", methods=['GET'])
def get_initial_data():
    '''returns a list of all available cities to populate the dropdown from which
    to select the group of cities to be used'''

    nodes = model.session.query(model.City).all()
    city_list = []
    for i in range(len(nodes)):
        city_list.append({'city': nodes[i].city, 'lat': nodes[i].lat, 'longitude': nodes[i].longitude, 'id': nodes[i].id,  'capital': nodes[i].capital})
    return json.dumps(city_list)



@app.route("/get_cities_data", methods=['POST'])
def get_cities_data():
    """returns list of cities + lat long as json, like:
    [ ("Annapolis", 34, 5), ("Austin", 2, 4)]
    """
    cities = request.form.getlist('city_group')
    nodes = []
    for city in cities:
        node = model.session.query(model.City).filter_by(id = int(city)+1).one()
        nodes.append(node)
    city_list = []
    for i in range(len(nodes)):
        city_list.append({'id': nodes[i].id, 'city': nodes[i].city, 'lat': nodes[i].lat, 'longitude': nodes[i].longitude})
    return json.dumps(city_list)

@app.route("/userinput", methods=['POST'])
def get_parameters():

    cycles = int(request.form['cycles'])
    algorithm = request.form['algorithm']
    start_temp = float(request.form['start_temp'])
    alpha = float(request.form['alpha'])
    move_operator = request.form['move_operator']
    start_city = int(request.form['start'])
    mode = request.form['mode']
    selected_cities = request.form['selected_cities']
    return_list = selected_cities.split(',')
    id_list = [] 
    current_score=[]
    animation_coords = []
    nodes2 = []
    animation_steps = []

    #Extract city ids and names into lists then look up coordinates and build
    #a dictionary with id as the key and a tuple of coordinates as the value
    for i in range(len(return_list)):
        if i%2 == 0:
            id_list.append(int(return_list[i]))

    for id in id_list:
        nodes2.append(model.session.query(model.City).filter_by(id = id).one())
    coords = tsp.read_coords_db(nodes2)

    i=0
    coord_dict = {}
    for id in id_list:
        coord_dict[id]=coords[i]
        i+= 1

    #Build the distance matrix. The distance matrix is of the form 
    #{(i, j): dist, ... (i,j): dist} 
    if mode == "as_the_crow_flies":
        matrix = tsp.distance_matrix2(coords, id_list)
    elif mode == "roads":
        matrix = tsp.road_matrix(coords, id_list)
    elif mode == "airline":
        matrix = tsp.air_matrix(coords, id_list)
    else:
        return "Error"

    #Choose our algorithm
    init_function =lambda: tsp.init_random_tour(id_list)#returns shuffled
    objective_function=lambda tour: -tsp.tour_length(matrix,tour) #note negation
    move_dict={"swapped_cities": tsp.swapped_cities, "reversed_sections": tsp.reversed_sections}

    if algorithm == "hillclimb":
        result = tsp.hillclimb(init_function, move_dict[move_operator], 
                objective_function, cycles)           
        num_evaluations, best_score, best, animation_steps, current_score = result

    elif algorithm == "hill_restart":
        result = tsp.hillclimb_and_restart(init_function, move_dict[move_operator], 
                objective_function, cycles)
        num_evaluations, best_score, best, animation_steps, current_score = result

    elif algorithm == "nearest":
        result = tsp.greedy(matrix, start_city)      
        num_evaluations, best_score, best = result

    elif algorithm == "annealing":
        result = tsp.anneal(init_function, move_dict[move_operator], objective_function,
            cycles,start_temp,alpha)
        num_evaluations, best_score, best, animation_steps, current_score = result
    else:
        print "error"
        return "error"
    
    tour_coords = tsp.drawtour_on_map2(coord_dict, best)

    #coordinates for each step
    
    for i in range(len(animation_steps)):
        animation_coords.append(tsp.drawtour_on_map2(coord_dict, animation_steps[i]))    

    tour_cities = convert_tour_to_city(best)

    if mode == "roads":
        poly_list, data = poly_line_tour2(best)
        poly_animation_steps = polyline_animation_steps2(animation_steps)
    else:
        poly_list = []
        poly_animation_steps = []

    results = {"iterations" : num_evaluations, "best_score" : best_score, "route" : best,
     "tour_coords": tour_coords, "tour_cities": tour_cities, "animation_coords": animation_coords, 
     "current_score": current_score, "poly_list": poly_list, "poly_animation_steps": poly_animation_steps}
    data = json.dumps(results)
    return data

def convert_tour_to_city(best):
    nodes = model.session.query(model.City).all()
    city_list = []
    for city in best:
        city_list.append(nodes[city-1].city)
    return city_list

def poly_line_tour(best):
    '''input best which is a list of nodes [i, j, k, l ... z] and return poly_list
    which is a list of polylines [line1, line2 .... linex] for 48 cities best
    includes each of the nodes from 0 to 47 once.'''

    poly_list = []
    for i in range(len(best)):
        city1 = best[i]
        city2 = best[(i+1)%len(best)]
        #This may be why it is running slow. Hard code? Change database??
        distance = model.session.query(model.Distance).filter_by(city1_id = city1).filter_by(city2_id = city2).first()

        polyline = distance.polyline
        poly_list.append(polyline)

    return poly_list

def poly_line_tour2(best):
    '''input best which is a list of nodes [i, j, k, l ... z] and return poly_list
    which is a list of polylines [line1, line2 .... linex] for 48 cities best
    includes each of the nodes from 0 to 47 once.'''
    total_data_call = 0
    poly_list = []
    global polyline_dict

    step_in = time.time()#step into the loop
    for i in range(len(best)):
        city1 = best[i]
        city2 = best[(i+1)%len(best)]
        lookup_string = str(city1)+'-'+str(city2)
        #This may be why it is running slow. Hard code? Change database??
        before_data_call = time.time()
        polyline = polyline_dict[lookup_string]
        
        after_data_call = time.time()
        total_data_call += (-before_data_call+after_data_call)
        
        
        poly_list.append(polyline)
    step_out = time.time()
    # print "returning each polyline tour2", (step_out - step_in)
    # print "total data call =", total_data_call
    return (poly_list, total_data_call)

def polyline_animation_steps(animation_steps):
    '''Converts animation steps (list of nodes) to polylines. Each polyline is a list of polyline segments.

    input: List of lists of nodes
    returns: List of lists of polylines
    '''

    poly_animation_steps = []
    for i in range(len(animation_steps)):
        line = poly_line_tour2(animation_steps[i])
        poly_animation_steps.append(line)

    return poly_animation_steps

def polyline_animation_steps2(animation_steps):
    '''Converts animation steps (list of nodes) to polylines. Each polyline is a list of polyline segments.
    
    input: List of lists of nodes
    returns: List of lists of polylines
    '''
    #1 call here may be slow here
    total = 0
    poly_animation_steps = []
    for i in range(len(animation_steps)):
        line, data = poly_line_tour2(animation_steps[i])
        poly_animation_steps.append(line)
        total += data
    # print total, "for getting data out of database"
    return poly_animation_steps

if __name__ == "__main__":

    PORT = int(os.environ.get("PORT", 5000))
    DEBUG = "NO_DEBUG" not in os.environ
    app.run(debug=DEBUG, host="0.0.0.0", port=PORT)  