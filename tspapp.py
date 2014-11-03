from flask import Flask, request, session, render_template, g, redirect, url_for, flash
import os
import jinja2
import tsp

app = Flask(__name__)
app.secret_key = '\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def index():
    '''cities are entered as tuples of x and y coordinates. 
      TO DO: generate random points.
      TO DO: generate distances using map data
    '''
     #Read in a coordinates file and print out the distance matrix for that file
    coord_file = open("cities48.txt")
    n = .09

    coords = tsp.read_coords(coord_file)
    matrix = tsp.cartesian_matrix(coords)

    #We begin our hill climb
    init_function =lambda: tsp.init_random_tour(len(coords))
    objective_function=lambda tour: -tsp.tour_length(matrix,tour) #note negation
    #result = tsp.hillclimb(init_function, tsp.reversed_sections, 
        # objective_function, 1000)
    result = tsp.hillclimb_and_restart(init_function, tsp.reversed_sections, 
        objective_function, 4000)
    num_evaluations, best_score, best = result

    #write to an image file
    tsp.write_tour_to_img(coords, best, n, "static/img/plot.png")
    return render_template("index.html", num_evaluations = num_evaluations,
        best_score = best_score, best = best)


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
    
    