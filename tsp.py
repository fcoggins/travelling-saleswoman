import math, random, logging
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
    print cities[0].city #Yay I have my data to be used here.
    coords=[]
    for i in range(len(cities)):
        x, y = cities[i].lat, -cities[i].longitude
        coords.append((float(x),float(y)))
    return coords
    

def cartesian_matrix(coords):
    '''Ceate a distance matrix for the city coordsthat uses straight line 
    distance. Input a list of (x,y) tuples and output a dictionary of the 
    distance between all pairs of cities.
    ex. matrix[1,2] will output the distance between city 1 and city 2. all
    distances are in the matrix twice from a to b and from b to a.
    '''
    matrix={}
    for i,(x1,y1) in enumerate(coords):
        for j,(x2,y2) in enumerate(coords):
            dx,dy=x1-x2,y1-y2
            dist=math.sqrt(dx*dx + dy*dy)
            matrix[i,j]=dist
    return matrix

def print_nice_matrix(matrix):
	'''Print a nice distance matrix that is readable by humans'''
	length = int(math.sqrt(len(matrix)))
	print length
	for i in range(length):
		for j in range (i+1, length):
			print "Distance from %d to %d is %0.0f"%(i, j, matrix[i,j])

def tour_length(matrix,tour):
    '''Calculate the length of any particular tour.
	Input a distance matrix and the list of cities as integers. Output the
	tour length as a float.
    '''
    total=0
    num_cities=len(tour)
    #print num_cities
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

def write_tour_to_img(coords,tour, n, img_file):

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


