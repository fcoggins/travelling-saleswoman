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

    current_score=[] #initialize here so that I don't get an error
    animation_coords = []

    nodes = model.session.query(model.City).all()
    coords = tsp.read_coords_db(nodes)
    #To calculate the distance matrix on the fly. This is faster for 48 capital
    #cities.
    matrix = tsp.distance_matrix(coords) 

    #Choose our algorithm
    init_function =lambda: tsp.init_random_tour(len(coords))
    objective_function=lambda tour: -tsp.tour_length(matrix,tour) #note negation
    animation_steps = []
    if algorithm == "hillclimb":
        result = tsp.hillclimb(init_function, tsp.reversed_sections, 
            objective_function, cycles)
        num_evaluations, best_score, best, animation_steps, current_score = result
    elif algorithm == "hill_restart":
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
    results = {"iterations" : num_evaluations, "best_score" : best_score, "route" : best,
     "tour_coords": tour_coords, "tour_cities": tour_cities, "animation_coords": animation_coords, 
     "current_score": current_score}
    data = json.dumps(results)
    return data

def convert_tour_to_city(best):
    nodes = model.session.query(model.City).all()
    city_list = []
    for city in best:
        city_list.append(nodes[city].city)
    return city_list


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)  