import math, random, logging, model


def read_coords_db(cities):
    '''in which data passes from Flask / SQLAlchemy to be used in the 
    coordinates file
    '''
    coords=[]
    for i in range(len(cities)):
        x, y = cities[i].lat, cities[i].longitude
        coords.append((float(x),float(y)))
    return coords

def distance_matrix2(coords, id_list):
    ''' Output a dictionary of the distance between chosen pairs of cities.
    '''
    matrix = {}
    # print coords
    for i in range(len(coords)):
        city1 = id_list[i]
        matrix[city1, city1]=0
        for j in range(len(coords)):           
            city2 = id_list[j]
            lat1, lon1, lat2, lon2 = coords[i][0], coords[i][1], coords[j][0], coords[j][1] 
            matrix[city1, city2]=distance_between_two_cities(lat1, lon1, lat2, lon2)
            matrix[city2, city1]=matrix[city1, city2]
        
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

def road_matrix(coords, id_list):
    '''This will pull data from the distance table into a matrix 
    to be used for tour length calculations. It will look like {(city1_id, city2_id):
    distance, (cityn_id, citym_id): distance, ...}.'''

    matrix = {}
    print id_list, "id list"
    for i in range(len(id_list)):
        city1 = id_list[i]
        matrix[city1, city1] = 0
        for j in range(i+1, len(id_list)):           
            city2 = id_list[j]
            print "city1:",city1, "city2:",city2
            miles = model.session.query(model.Distance).filter(model.Distance.city1_id == city1).\
                filter(model.Distance.city2_id == city2).first()
            print miles
            matrix[city1, city2] = miles.road_miles
            matrix[city2, city1] = matrix[city1, city2]
    return matrix

def air_matrix(coords, id_list):
    '''Will create a matrix of edge weights based on the optimum combination of 
    flight cost and travel time.

    Input: coords and list of selected cities.
    Output:  dictionary like {(city1_id, city2_id):optimum edge weight, 
    (cityn_id, citym_id): distance, ...}.

    Formula for calculating edge weight is min(flight cost + travel time/60 * 30)

    '''

    matrix = {}

    for i in range(len(id_list)):
        city1 = id_list[i]
        matrix[city1, city1] = 0
        for j in range(len(id_list)):           
            city2 = id_list[j]
            if city1 == city2:
                continue
            edge_weight = []
            result = model.session.query(model.Distance).filter(model.Distance.city1_id == city1).\
                filter(model.Distance.city2_id == city2).first()

            add_edge_weight(edge_weight, result.cost1, result.time1)
            add_edge_weight(edge_weight, result.cost2, result.time2)
            add_edge_weight(edge_weight, result.cost3, result.time3)
            add_edge_weight(edge_weight, result.cost4, result.time4)
            add_edge_weight(edge_weight, result.cost5, result.time5)
            add_edge_weight(edge_weight, result.cost6, result.time6)
            add_edge_weight(edge_weight, result.cost7, result.time7)
            add_edge_weight(edge_weight, result.cost8, result.time8)
            add_edge_weight(edge_weight, result.cost9, result.time9)
            add_edge_weight(edge_weight, result.cost10, result.time10)

            #print i, j, miles.miles
            if edge_weight:
                matrix[city1, city2] = min(edge_weight)#minimum of the ten options
            else:
                matrix[city1, city2] = 500 #No flights...(Topeka, Trenton)

    return matrix

def add_edge_weight(edge_weight, cost1, time1):
    if cost1:
        edge_weight.append(cost1 + time1/2)
    return edge_weight

def print_nice_matrix(matrix, id_list):
    '''Print a nice distance matrix that is readable by humans. Used for debugging'''

    for i in range(len(id_list)):
        city1 = id_list[i]
    	for j in range (len(id_list)):
            city2 = id_list[j]
            print "Distance from %d to %d is %0.0f"%(city1, city2, matrix[(city1, city2)])


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


def drawtour_on_map2(coord_dict, tour):
    '''return a list of tuples to use in drawing on map. Each tuple represents
    a tour segment.
    '''

    list_of_tour_segments = []

    for city in tour:
        list_of_tour_segments.append(coord_dict[city])
    return list_of_tour_segments


def init_random_tour(tour):
    '''Takes selected tour as an arguement and returns a random tour'''
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
    animation_steps = [best] #keep track of intermediate tour routes
    current_score = [best_score] #keep track of intermediate scores
    
    while num_evaluations < max_evaluations:
        # If we append here we will show the total animation steps (minus last one
        # but this makes for a more boring animation.) Clicking stop gives best solution.
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

        #if we append here we are only appending those steps that are improvements
        #to the animation which speeds it up. This works for basic hillclimb but
        #not for hillclimb and restart, which stops the animation at only one try.
        #animation steps that are not improvements are not shown in the count.
        animation_steps.append(best)
        current_score.append(best_score)
    return (num_evaluations,best_score,best, animation_steps, current_score)

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
    animation_steps_total = []
    while num_evaluations < max_evaluations:
        remaining_evaluations=max_evaluations-num_evaluations
        
        evaluated,score,found, animation_steps, current_score=hillclimb(
            init_function,
            move_operator,
            objective_function,
            remaining_evaluations)
        
        num_evaluations+=evaluated
        animation_steps_total+=animation_steps

        if score > best_score or best is None:
            best_score=score
            best=found
    animation_steps_total+=[best]       
    return (num_evaluations,best_score,best,animation_steps_total, current_score)


#Nearest Neighbor algorithm
def greedy(dist, start_city):
    '''solve using the greedy algorithm.'''

    city_tuples=dist.keys()
    unvisited_cities_list = []
    for item in city_tuples:
        unvisited_cities_list+=(list(item))
    unvisited_cities = set(unvisited_cities_list)
    current_city = start_city
    unvisited_cities.remove(current_city)#remove current city from the set of unvisited cities
    solution = [current_city]

    def distance_from_current_city(to):
        return dist[(current_city, to)]

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
        self.steps=[]
        self.score_list=[]
    
    def __call__(self,solution):
        self.steps.append(solution)       
        score=self.objective_function(solution)
        self.score_list.append(score)
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

    # print 'anneal started: score=%f'%current_score
    
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
    
    best_score=objective_function.best_score #This is the final route (miles)
    best=objective_function.best #Nodes that make up the best route
    score_list=objective_function.score_list
    objective_function.steps.append(best)

    #print 'anneal finished: num_evaluations=%d, best_score=%f'%num_evaluations,best_score
    return (num_evaluations,best_score,best, objective_function.steps, score_list)




