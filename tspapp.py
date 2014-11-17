from flask import Flask, request, session as fsksession, render_template, g, redirect, url_for, flash
import os, jinja2, random, string, json, sys
import tsp, model
#import credentials

app = Flask(__name__)
app.secret_key = '\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def index():
    """Return the index page"""  
    return render_template("index2.html")

@app.route("/get_cities_data", methods=['GET'])
def get_cities_data():
    """returns list of cities + lat long as json, like:
    [ ("Annapolis", 34, 5), ("Austin", 2, 4)]
    """
    nodes = model.session.query(model.City).all()
    city_list = []
    for i in range(len(nodes)):
        city_list.append({'city': nodes[i].city, 'lat': nodes[i].lat, 'longitude': nodes[i].longitude})
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

    current_score=[] #initialize here so that I don't get an error
    animation_coords = []

    nodes = model.session.query(model.City).all()
    coords = tsp.read_coords_db(nodes)

    #The distance matrix is of the form {(i, j): dist, ... (i,j): dist} where i and
    #j are between 0 and the number of nodes. In the 48 cities data the city_id is
    #from one to the number of nodes(inclusive) 1 - 48 and the relationship is city_id = i + 1.
    if mode == "as_the_crow_flies":
        matrix = tsp.distance_matrix(coords)
    elif mode == "roads":
        matrix = tsp.road_matrix() 
    else:
        return "Error"

    #Choose our algorithm
    init_function =lambda: tsp.init_random_tour(len(coords))
    objective_function=lambda tour: -tsp.tour_length(matrix,tour) #note negation
    animation_steps = []
    if algorithm == "hillclimb":
        if move_operator == 'swapped_cities':
            result = tsp.hillclimb(init_function, tsp.swapped_cities, 
                objective_function, cycles)
            num_evaluations, best_score, best, animation_steps, current_score = result
        else:
            result = tsp.hillclimb(init_function, tsp.reversed_sections, 
                objective_function, cycles)
            num_evaluations, best_score, best, animation_steps, current_score = result
    #hillclimb and restart doesn't show the entire algorithm, just the last one I think.
    #put some thought into how to display this.
    elif algorithm == "hill_restart":
        if move_operator == 'swapped_cities':
            result = tsp.hillclimb_and_restart(init_function, tsp.swapped_cities, 
                objective_function, cycles)
            num_evaluations, best_score, best, animation_steps, current_score = result
        else:
            result = tsp.hillclimb_and_restart(init_function, tsp.reversed_sections, 
                objective_function, cycles)
            num_evaluations, best_score, best, animation_steps, current_score = result

    elif algorithm == "nearest":
        result = tsp.greedy(matrix, start_city)      
        num_evaluations, best_score, best = result
    elif algorithm == "annealing":
        if move_operator == 'swapped_cities':
            result = tsp.anneal(init_function, tsp.swapped_cities, objective_function,
            cycles,start_temp,alpha)
            num_evaluations, best_score, best, animation_steps, current_score = result
        else:
            result = tsp.anneal(init_function, tsp.reversed_sections, objective_function,
            cycles,start_temp,alpha)
            num_evaluations, best_score, best, animation_steps, current_score = result
    else:
        print "error"
        return "error"
    
    #write to map
    #coordinates for a single tour
    tour_coords = tsp.drawtour_on_map(coords,best)

    #coordinates for each step
    
    for i in range(len(animation_steps)):
        animation_coords.append(tsp.drawtour_on_map(coords, animation_steps[i]))    

    #return results as JSON
    tour_cities = convert_tour_to_city(best)
    if mode == "roads":
        poly_list = poly_line_tour(best)
    else:
        poly_list = []

    results = {"iterations" : num_evaluations, "best_score" : best_score, "route" : best,
     "tour_coords": tour_coords, "tour_cities": tour_cities, "animation_coords": animation_coords, 
     "current_score": current_score, "poly_list": poly_list}
    data = json.dumps(results)
    return data

def convert_tour_to_city(best):
    nodes = model.session.query(model.City).all()
    city_list = []
    for city in best:
        city_list.append(nodes[city].city)
    return city_list

def poly_line_tour(best):
    '''input best which is a list of nodes [i, j, k, l ... z] and return poly_list
    which is a list of polylines [line1, line2 .... linex] for 48 cities best
    includes each of the nodes from 0 to 47 once.'''

    print best
    poly_list = []
    for i in range(len(best)):
        city1 = best[i]+1
        city2 = best[(i+1)%len(best)]+1

        distance = model.session.query(model.Distance).filter_by(city1_id = city1).filter_by(city2_id = city2).first()
        #dist_object = model.session.query(model.Distance).filter_by(city1_id=i,city2_id=j).first()

        polyline = distance.polyline
        poly_list.append(polyline)

    #We need to build our polylist and put into database
    print poly_list
    return poly_list


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)  