from flask import Flask, request, session as fsksession, render_template, g, redirect, url_for, flash
import os, jinja2, random, string, json
import tsp, model

app = Flask(__name__)
app.secret_key = '\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def index():
    """Return the index page"""  
    return render_template("index.html")

@app.route("/index2")
def index2():
    """Now let's add the map to the page"""
    #pulling stuff from database, the two statements below actually need to
    #happen later when processing the form input

    #nodes = model.session.query(model.City).all()
    #tsp.read_coords_db(nodes)

    return render_template("index2.html")



@app.route("/get_cities_data", methods=['GET'])
def get_cities_data():
    """returns list of cities + lat long as json, like:
    [ ("Annapolis", 34, 5), ("Austin", 2, 4)]
    """
    nodes = model.session.query(model.City).all()
    print len(nodes)
    city_list = []
    for i in range(len(nodes)):
        city_list.append({'city': nodes[i].city, 'lat': nodes[i].lat, 'longitude': nodes[i].longitude})
        print city_list
    return json.dumps(city_list)

@app.route("/userinput", methods=['POST'])
def get_parameters():

    filename = request.form['data']
    n = float(request.form['scaling'])
    cycles = int(request.form['cycles'])
    algorithm = request.form['algorithm']
    
    if filename == "GMdata":
        nodes = model.session.query(model.City).all()
        coords = tsp.read_coords_db(nodes)
        matrix = tsp.distance_matrix(coords)

    else:
        coord_file = open(filename)
        coords = tsp.read_coords(coord_file)
        matrix = tsp.cartesian_matrix(coords)   

    #We begin our hill climb
    init_function =lambda: tsp.init_random_tour(len(coords))
    objective_function=lambda tour: -tsp.tour_length(matrix,tour) #note negation
    if algorithm == "hillclimb":
        result = tsp.hillclimb(init_function, tsp.reversed_sections, 
            objective_function, cycles)
    else:
        result = tsp.hillclimb_and_restart(init_function, tsp.reversed_sections, 
            objective_function, cycles)

    num_evaluations, best_score, best = result

  
    #generate a new image file name

    img_file = ''.join(random.choice(string.ascii_lowercase) for i in range(7))
    img_file = 'static/img/' + img_file + '.png'

    #write to an image file

    tsp.write_tour_to_img(coords, best, n, img_file)

    #return results as JSON

    results = {"iterations" : num_evaluations, "best_score" : best_score, "route" : best,
    "img_file" : img_file}
    data = json.dumps(results)
    return data



if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)  