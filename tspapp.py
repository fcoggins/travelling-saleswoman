from flask import Flask, request, session as fsksession, render_template, g, redirect, url_for, flash
import os, jinja2, random, string, json, sys
import tsp, model

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

    nodes = model.session.query(model.City).all()
    coords = tsp.read_coords_db(nodes)
    #To calculate the distance matrix on the fly. This is faster for 48 capital
    #cities.
    matrix = tsp.distance_matrix(coords) 

    #Choose our algorithm
    init_function =lambda: tsp.init_random_tour(len(coords))
    objective_function=lambda tour: -tsp.tour_length(matrix,tour) #note negation
    if algorithm == "hillclimb":
        result = tsp.hillclimb(init_function, tsp.reversed_sections, 
            objective_function, cycles)
    elif algorithm == "hill_restart":
        result = tsp.hillclimb_and_restart(init_function, tsp.reversed_sections, 
            objective_function, cycles)
    elif algorithm == "nearest":
        result = tsp.greedy(matrix)
    elif algorithm == "annealing":
        result = tsp.anneal(init_function, tsp.reversed_sections, objective_function,
            cycles,start_temp,alpha)
    else:
        print "error"
        return "error"

    num_evaluations, best_score, best = result

    #write to map

    tour_coords = tsp.drawtour_on_map(coords,best)

    #return results as JSON

    results = {"iterations" : num_evaluations, "best_score" : best_score, "route" : best,
     "tour_coords": tour_coords}
    data = json.dumps(results)
    return data

def run_anneal(init_function,move_operator,objective_function,max_iterations,start_temp,alpha):
    if start_temp is None or alpha is None:
        print "missing --cooling start_temp:alpha for annealing"
        sys.exit(1)
    iterations,score,best=tsp.anneal(init_function,move_operator,objective_function,max_iterations,start_temp,alpha)
    return iterations,score,best

if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)  