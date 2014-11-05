from flask import Flask, request, session, render_template, g, redirect, url_for, flash
import os, jinja2, random, string, json
import tsp

app = Flask(__name__)
app.secret_key = '\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def index():
    """Return the index page"""  
    return render_template("index.html")

@app.route("/userinput", methods=['POST'])
def get_parameters():

    filename = request.form['data']
    n = float(request.form['scaling'])
    cycles = int(request.form['cycles'])
    algorithm = request.form['algorithm']
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