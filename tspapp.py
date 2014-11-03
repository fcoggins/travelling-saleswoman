from flask import Flask, request, session, render_template, g, redirect, url_for, flash
import os
import jinja2
import tsp

app = Flask(__name__)
app.secret_key = '\xf5!\x07!qj\xa4\x08\xc6\xf8\n\x8a\x95m\xe2\x04g\xbb\x98|U\xa2f\x03'
app.jinja_env.undefined = jinja2.StrictUndefined

@app.route("/")
def index():
    """This is the 'cover' page"""
    return render_template("index.html")


if __name__ == "__main__":
    '''cities are entered as tuples of x and y coordinates. 
      TO DO: generate random points.
      TO DO: generate distances using map data
    '''
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
    
    #Read in a coordinates file and print out the distance matrix for that file
    coord_file = open("cities10.txt")
    city_coords = tsp.read_coords(coord_file)
    dist_matrix = tsp.cartesian_matrix(city_coords)
    tsp.print_nice_matrix(dist_matrix)

    #Print the length of any particular route
    city_list = [0, 1, 2, 3, 4, 5, 6, 7]
    a_route_length = tsp.tour_length(dist_matrix, city_list)
    print a_route_length

    #Print all permutations where exactly 2 cities in a list are swapped.
    for tour in tsp.swapped_cities(city_list):
        print tour
        pass

    print "***********"

    #Print all permutations where exactly 2 edges in a list are swapped.
    for tour in tsp.reversed_sections(city_list):
        print tour
        pass

    #write to an image file
    tsp.write_tour_to_img(city_coords, city_list, "static/img/plot.png")