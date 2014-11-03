import math, random
from PIL import Image, ImageFont, ImageDraw

def read_coords(coord_file):
    '''Read coordinates from a text file. One x, y coordinate per line''' 
    coords=[]
    for line in coord_file:
        line=line.strip().split(' ')
        x, y = line[1], line[2]
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

def write_tour_to_img(coords,tour,img_file):

    #scale coordinates
    n = 0.2
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


