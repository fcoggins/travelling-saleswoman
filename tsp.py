import math, random, logging, model
from PIL import Image, ImageFont, ImageDraw

def read_coords(coord_file):
    '''Read coordinates from a text file. One x, y coordinate per line''' 
    coords=[]
    for line in coord_file:
        line=line.strip().split(' ')
        x, y = line[1], line[2]
        coords.append((float(x),float(y)))
    return coords

def read_coords_db(cities):
    '''in which data passes from Flask / SQLAlchemy to be used in the 
    coordinates file
    '''
    coords=[]
    for i in range(len(cities)):
        x, y = cities[i].lat, cities[i].longitude
        coords.append((float(x),float(y)))
    return coords
    

def cartesian_matrix(coords):
    '''Create a distance matrix for the city coordsthat uses straight line 
    distance. Input a list of (x,y) tuples and output a dictionary of the 
    distance between all pairs of cities.
    ex. matrix[1][2] will output the distance between city 1 and city 2. all
    distances are in the matrix twice from a to b and from b to a.
    '''
    matrix={}
    for i,(x1,y1) in enumerate(coords):
        for j,(x2,y2) in enumerate(coords):
            dx,dy=x1-x2,y1-y2
            dist=math.sqrt(dx*dx + dy*dy)
            matrix[i,j]=dist
    return matrix

def distance_matrix(coords):
    ''' Output a dictionary of the distance between all pairs of cities. As above
    but we have the option of using our own functions to calculate the distance
    '''
    matrix = {}

    for i,(lat1,lon1) in enumerate(coords):
        for j,(lat2,lon2) in enumerate(coords): 
            matrix[i,j]=distance_between_two_cities(lat1, lon1, lat2, lon2)
    return matrix

def distance_between_two_cities(lat1, lon1, lat2, lon2):
    '''Calculates distance between two points using the spherical law of cosines.
    Input is (lat, long) for city one and (lat, long) for city two.'''

    R = 6371
    a = 0.5 - math.cos((lat2 - lat1) * math.pi / 180)/2 + \
        math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * \
        (1 - math.cos((lon2 - lon1) * math.pi / 180))/2
    dist = R * 2 * math.asin(math.sqrt(a)) * 0.621371 #convert to miles
    return dist

def distance_matrix_from_db():
    '''This will pull data from our database table of 48 us cities into a matrix 
    to be used for tour length calculations. It will look like {(city1_id, city2_id):
    distance, (cityn_id, citym_id): distance, ...}. This is done to avoid recalculating
    distances each time an algorithm is called'''

    matrix = {}
    distances = model.session.query(model.Distance).all()
    length = int(math.sqrt(len(distances)))
    #since this is a symetric problem we only have to calculate the matrix from i to j
    #and not from j to i. However, tour length only looks for the tuple which is the key
    #in on direction so we may have to build the second half of the matrix.
    for i in range(length):
        for j in range(i+1, length):
            city1 = i + 1
            city2 = j + 1
            miles = model.session.query(model.Distance).filter(model.Distance.city1_id == city1).\
                filter(model.Distance.city2_id == city2).first()
            #print i, j, miles.miles
            matrix[(i, j)] = miles.miles
            matrix[(j, i)] = matrix[(i, j)]
    #print_nice_matrix(matrix)
    return matrix

def print_nice_matrix(matrix):
    '''Print a nice distance matrix that is readable by humans. Used for debugging'''

    print len(matrix)
    print math.sqrt(len(matrix))
    length = int(math.sqrt(len(matrix)))
    print length
    for i in range(length):
    	for j in range (i+1, length):
    		print "Distance from %d to %d is %0.0f"%(i, j, matrix[i,j])

def look_up_distance(city1, city2):
    '''Look up the distance between any two cities from the database. This does 
    the look up one at a time and slows the program way down as opposed to having 
    the matrix in memory.'''

    #For our model, city id's are the indexed id's + 1
    city1 += 1
    city2 += 1
    #Look it up and return
    distances = model.session.query(model.Distance).filter(model.Distance.city1_id == city1).\
        filter(model.Distance.city2_id == city2).one()
    return distances.miles

def tour_length(matrix,tour):
    '''Calculate the length of any particular tour.
	Input a distance matrix and the list of cities as integers. Output the
	tour length as a float.
    '''
    total=0
    num_cities=len(tour)
    for i in range(num_cities):
        j=(i+1)%num_cities
        city_i=tour[i]
        city_j=tour[j]
        total+=matrix[city_i,city_j]
    return total


def all_pairs(size,shuffle=random.shuffle):
    r1=range(size)
    r2=range(size)
    if shuffle:
        shuffle(r1)
        shuffle(r2)
    for i in r1:
        for j in r2:
            #here yield returns a function
            yield (i,j)

def swapped_cities(tour):
    '''generator to create all possible variations
      where two cities have been swapped.
      Input is a list of cities. Output is a function that yeilds a list where 
      exactly two of the cities in the original list have been swapped. '''

    for i,j in all_pairs(len(tour)):
        if i < j:
            copy=tour[:]
            copy[i],copy[j]=tour[j],tour[i]
            yield copy

def reversed_sections(tour):
    '''generator to return all possible variations 
      where the section between two cities are swapped. Will include variations
      where the tour looks the same but starting at a different node. Does not 
      include the same tour in the opposite direction. '''

    for i,j in all_pairs(len(tour)):
        if i != j:
            copy=tour[:]
            if i < j:
                copy[i:j+1]=reversed(tour[i:j+1])
            else:
                copy[i+1:]=reversed(tour[:j])
                copy[:j]=reversed(tour[i+1:])
            if copy != tour: # no point returning the same tour
                yield copy

def write_tour_to_img(coords, tour, n, img_file):

    #scale coordinates by n
    coords=[(x*n,y*n) for (x,y) in coords]

    num_cities=len(tour)

    padding=20
    # shift all coords in a bit and scale by n
    coords=[(x+padding,y+padding) for (x,y) in coords]
    maxx,maxy=0,0
    for x,y in coords:
        maxx=max(x,maxx)
        maxy=max(y,maxy)
    maxx+=padding
    maxy+=padding
    img=Image.new("RGB",(int(maxx),int(maxy)),color=(255,255,255))
    
    font=ImageFont.load_default()
    d=ImageDraw.Draw(img);
    
    for i in range(num_cities):
        j=(i+1)%num_cities
        city_i=tour[i]
        city_j=tour[j]
        x1,y1=coords[city_i]
        x2,y2=coords[city_j]
        d.line((int(x1),int(y1),int(x2),int(y2)),fill=(0,0,0))
        d.text((int(x1)+7,int(y1)-5),str(i),font=font,fill=(32,32,32))
    
    
    for x,y in coords:
        x,y=int(x),int(y)
        d.ellipse((x-5,y-5,x+5,y+5),outline=(0,0,0),fill=(196,196,196))
    del d
    img.save(img_file, "PNG")

def drawtour_on_map(coords, tour):
    '''return a list of tuples to use in drawing on map. Each tuple represents
    a tour segment.
    '''
    num_cities = len(tour)
    list_of_tour_segments = []

    for i in range(num_cities):
        city_i=tour[i]
        list_of_tour_segments.append(coords[city_i])
    return list_of_tour_segments


def init_random_tour(tour_length):
    '''Takes tour length as an arguement and returns a random tour'''
    tour=range(tour_length)
    random.shuffle(tour)
    return tour

def hillclimb(
    init_function,
    move_operator,
    objective_function,
    max_evaluations):
    '''
    hillclimb until either max_evaluations
    is reached or we are at a local optima
    '''
    best=init_function()
    best_score=objective_function(best)
    
    num_evaluations=1

    logging.info('hillclimb started: score=%f',best_score)
    
    while num_evaluations < max_evaluations:
        # examine moves around our current position
        move_made=False
        for next in move_operator(best):
            if num_evaluations >= max_evaluations:
                break
            
            # see if this move is better than the current
            next_score=objective_function(next)
            num_evaluations+=1
            if next_score > best_score:
                best=next
                best_score=next_score
                move_made=True
                break # depth first search
            
        if not move_made:
            break # we couldn't find a better move 
                     # (must be at a local maximum)
    logging.info('hillclimb finished: num_evaluations=%d, best_score=%f',num_evaluations,best_score)
    return (num_evaluations,best_score,best)

def hillclimb_and_restart(
    init_function,
    move_operator,
    objective_function,
    max_evaluations):
    '''
    repeatedly hillclimb until max_evaluations is reached
    '''
    best=None
    best_score=0
    
    num_evaluations=0
    while num_evaluations < max_evaluations:
        remaining_evaluations=max_evaluations-num_evaluations
        
        evaluated,score,found=hillclimb(
            init_function,
            move_operator,
            objective_function,
            remaining_evaluations)
        
        num_evaluations+=evaluated
        if score > best_score or best is None:
            best_score=score
            best=found
        
    return (num_evaluations,best_score,best)


#Nearest Neighbor algorithm
def greedy(dist):
    '''solve using the greedy algorithm.'''
    n = int(math.sqrt(len(dist)))

    current_city = 0
    unvisited_cities = set(range(1, n))
    solution = [current_city]

    def distance_from_current_city(to):
        return dist[current_city, to]

    while unvisited_cities:

        next_city = min(unvisited_cities, key=distance_from_current_city)
        unvisited_cities.remove(next_city)
        solution.append(next_city)
        current_city = next_city
    length = tour_length(dist, solution)
    return (None, length, solution)


#Simulated Annealing

def P(prev_score,next_score,temperature):
    '''The probability function for deciding whether to move from previous 
    score to next score. If the next score is better we always accept it. This
    function will select solutions closer to the current solution with a high 
    probability. Temperature is used to vary the probability. At higher temperatures,
    probability will be higher. At lower temperature, as the function cools,
    probabilities are lower.
    '''

    if next_score > prev_score:
        return 1.0
    else:
        return math.exp( -abs(next_score-prev_score)/temperature )


def kirkpatrick_cooling(start_temp,alpha):
    '''This is a generator function that determines how the temperature will drop
    off. The temperature drops off quickly then decreases slowly. Alpha is less
    than 1.'''

    T=start_temp
    while True:
        yield T
        T=alpha*T

class ObjectiveFunction:
    '''class to wrap an objective function and 
    keep track of the best solution evaluated'''
    def __init__(self,objective_function):
        self.objective_function=objective_function
        self.best=None
        self.best_score=None
    
    def __call__(self,solution):
        score=self.objective_function(solution)
        if self.best is None or score > self.best_score:
            self.best_score=score
            self.best=solution
        return score

def anneal(init_function,move_operator,objective_function,max_evaluations,
    start_temp,alpha):
    '''Initialization function (we could use random but why not try nearest neighbor).
    The move operator could be reversed_sections or swapped_cities. alpha should be
    less than 1. Start temperature and alpha can be varied and the optimum can be reached
    through experimentation.
    '''
    
    # wrap the objective function (so we record the best)
    objective_function=ObjectiveFunction(objective_function)
    
    current=init_function()
    current_score=objective_function(current)
    num_evaluations=1
    
    cooling_schedule=kirkpatrick_cooling(start_temp,alpha)

    print 'anneal started: score=%f'%current_score
    
    for temperature in cooling_schedule:
        done = False
        # examine moves around our current position
        for next in move_operator(current):
            if num_evaluations >= max_evaluations:
                done=True
                break
            
            next_score=objective_function(next)
            num_evaluations+=1
            
            # probablistically accept this solution
            # always accepting better solutions
            p=P(current_score,next_score,temperature)
            if random.random() < p:
                current=next
                current_score=next_score
                break
        # see if completely finished
        if done: break
    
    best_score=objective_function.best_score
    best=objective_function.best
    #print 'final temperature: %f'%temperature
    #print num_evaluations, best_score
    #print 'anneal finished: num_evaluations=%d, best_score=%f'%num_evaluations,best_score
    return (num_evaluations,best_score,best)




