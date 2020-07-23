import numpy as np
from stl import mesh
import matplotlib.pyplot as plt
import json
from json import JSONEncoder
import time
import copy
import pprint

class vector(JSONEncoder):
    def __init__(self, start, stop):
        self.start = [round(point, 3) for point in start]
        self.stop = [round(point, 3) for point in stop]
        self.bisect_point = [1/2*(start[0] + stop[0]), 1/2*(start[1]+stop[1])]
        if (stop[1]-start[1]) == 0:
            self.normal_angle = 'inf'
        else:
            self.normal_angle = -((stop[0]-start[0])/(stop[1]-start[1]))


    def contains(self, start, stop):
        return (self.start == start and self.stop == stop) or (self.stop == start and self.start == stop)
    
    def __str__(self):
        return str(self.start) + ", " + str(self.stop)

    def default(self, o):
        return o.__dict__
    def __repr__(self):
        return repr(str(self.start) + ", " + str(self.stop))
    def swap_points(self):
        temp = self.stop
        self.stop = self.start
        self.start = temp
    def toJSON(self):
        return json.dumps(self, default = lambda o: o.__dict__,
        sort_keys=True, indent=4)


# xy_coords = []
# for coord in points:
#     if coord[2] == 0:
#         xy_coords.append(coord.tolist())


# returns the xy triangles that make up a stl shape.
# param = a list of vectors from a mesh
def extract_xy_triangles(vectors):
    if vectors.shape[-2:]!=(3, 3):
        raise Exception("wrong format")
    xy_faces = []
    add = False
    for face in vectors:
        for vector in face:
            if int(vector[2]) != 0:
                add = False
                break
            else:
                add = True
        if add:
            faces = []
            for vertex in face:
                faces.append(vertex[0:2].tolist())
            xy_faces.append(faces)
        add = False

    return xy_faces
            
# saves a png in the current directory of the xy vector plot of a given stl file.
# param = list of mesh vectors and a file name to save it under
def plot_xy(meshvectors, filename = None):
    if filename == None:
        filename = input("Enter output file name: ")
    faces = extract_xy_triangles(meshvectors)
    for face in faces:
        x = []
        y = []
        for vector in face:
            x.append(vector[0])
            y.append(vector[1])
        x.append(face[0][0])
        y.append(face[0][1])
        plt.plot(x,y)
    plt.savefig(filename + ".png")

    open_img = input("open image (y/n)?")
    if open_img == 'y':
        plt.show()

# plots and saves a png of point pairs as opposed to a group of triangles like plot_xy
# param = a list of x,y vectors
def plot_vectors(vectors):
    if isinstance(vectors[0], list):
        vecs = []
        for sublist in vectors:
            for item in sublist:
                vecs.append(item)
    else:
        vecs = vectors
    
    x = []
    y = []
    for points in vecs:
        x.append(points.start[0])
        x.append(points.stop[0])
        y.append(points.start[1])
        y.append(points.stop[1])
        plt.plot(x,y)
        x = []
        y = []
    plt.savefig(filename + ".png")
    open_img = input("open image (y/n)?")
    if open_img == 'y':
        plt.show()
    
# takes many faces of a triangle represented by points and returns a list of vectors connecting each individual triangles points
# param = a list of 2d faces
def convert_to_vectors(xy_faces):
    vectors = []
    for face in xy_faces:
        for i in range(2):
            vectors.append(vector(face[i], face[i+1]))
        vectors.append(vector(face[2], face[0]))
    return vectors

# removes vectors that start or stop at the same two points
# param = a list of xy_vectors
def remove_duplicate_vectors(xy_vectors):
    removed = []
    non_dup_vectors = []

    for v1 in xy_vectors:
        for v2 in non_dup_vectors:
            if v2.contains(v1.start, v1.stop):
                removed.append(v1)
        non_dup_vectors.append(v1)

    for v1 in removed:
        i = 0
        while i < len(non_dup_vectors):
            if non_dup_vectors[i].contains(v1.start, v1.stop):
                non_dup_vectors.remove(non_dup_vectors[i])
            else:
                i+=1
    
    return non_dup_vectors

# outputs 2d vectors to a JSON file in the form of a dctionary. vector_# --> vector start and stop
# param = a list of vectors  
def to_json(shapes):
    shape_list = []
    for shape in shapes:
        vectors = []
        for vector in shape:
            vectors.append([vector.start, vector.stop])
        shape_list.append(vectors)
    names = []
    for i in range(len(shapes)):
        names.append('shape_'+str(i+1))
    data = dict(zip(names, shape_list))
    with open('vectors.json', 'w') as outfile:
        json.dump(data, outfile, indent=4, separators=(',',':'))

# taken from github
# input are two lists of two lists representing start and stop x y coords
def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
       print(Exception('lines do not intersect'))
    else:
        d = (det(*line1), det(*line2))
        x = round(det(d, xdiff) / div, 2)
        y = round(det(d, ydiff) / div, 2)
        return x, y

# read in a json and return it as a dictionary
def read_json(filename):
    with open('/home/adanfo/Documents/vscode/' + filename) as f:
        data = json.load(f)
    return data


def bisecting_line(vector):
    point1 = vector.bisect_point
    if vector.normal_angle == 'inf':
        point2 = [vector.bisect_point[0], vector.bisect_point[1]-1]
    else:
        point2 = [vector.bisect_point[0]+1, vector.bisect_point[1]+vector.normal_angle]
    return [point1, point2]

# takes a list of vectors and returns the same list with connected vectors such that it creates one long path
# WARNING: it only works now with stl files that are completely connected, so words will not work peoperly at the moment
# param: list of vector objects
def connect_vectors(vectors):
    vectors_copy = copy.copy(vectors)
    cur = vectors_copy.pop(0)
    organized = []
    package = []
    package.append(cur)
    while len(vectors_copy) != 0:
        arc_start = cur.start
        arc_stop = cur.stop
        package_len = len(package)
        for i in range(len(vectors_copy)):
            cur = vectors_copy[i]
            start = cur.start
            stop = cur.stop
            if start == arc_stop or stop == arc_stop:
                if stop == arc_stop:
                    cur.swap_points()
                package.append(cur)
                arc_stop = cur.stop
                del vectors_copy[i]
                break
            elif stop == arc_start or start == arc_start:
                if start == arc_start:
                    cur.swap_points
                package.insert(0, cur)
                arc_start = cur.start
                del vectors_copy[i]
                break
        if package_len == len(package):
            organized.append(package)
            package = []   
            cur = vectors_copy.pop(0)
            package.append(cur)
    organized.append(package)
    return organized

if __name__ == "__main__":
    filename = "teardrop"
    cube = mesh.Mesh.from_file("/home/adanfo/Documents/stl_testing/" + filename + '.stl')
    # mesh.Mesh.from_file("/home/adanfo/Documents/stl_testing/"+ input("Enter file name: ") +".stl")
    points = np.around(np.unique(cube.vectors.reshape([cube.vectors.size//3, 3]), axis=0),2)
    # print("Points are", points.tolist())

    # print(cube.normals)
    # print(cube.vectors.shape[-2:])
    faces = extract_xy_triangles(cube.vectors)

    vectors = remove_duplicate_vectors(convert_to_vectors(faces))

    connected = connect_vectors(vectors)
    to_json(connected)
    json = read_json('vectors.json')
    plot_vectors(connected)


    # v = vector([1,2], [3,4])
    # print(v.toJSON())


    # organized_vectors = organize_vectors(vectors)
    # plot_vectors(vectors)
    # print(len(vectors))
    # print(len(organized_vectors))
    # for vector in organized_vectors:
    #     print(vector)



    # for vector in organized_vectors:
    #     print(vector)

        
    # for i in range(1, len(vectors)):
    #     print('vector #:' + str(i), end = '\n')
    #     if vectors[i-1].normal_angle == 'inf' or vectors[i].normal_angle:
    #         print(line_intersection(bisecting_line(vectors[i-1]), bisecting_line(vectors[i])))
    #     elif round(vectors[i-1].normal_angle, 4) == round(vectors[i].normal_angle, 4):
    #         print(str(vectors[i].normal_angle) + "\nparallel")
    #     else:
    #         print(line_intersection(bisecting_line(vectors[i-1]), bisecting_line(vectors[i])))
        


    # for vector in vectors:
    #     print(vector)



    # to_json(vectors)

    # print(vectors)

    # for i in convert_to_vectors(faces):
    #     print(i)


    # for i in vectors:
    #     print(i)




    # plot_xy(cube.vectors, "yeet")
    # plot_xy(cube.vectors)

            

    # plt.plot(faces[0][0])
    # plt.plot(faces[0][1])
    # plt.plot(faces[0][2])



    # for face in faces:
    #     print(face, end = '\n')
    # print("xy points are", xy_coords)
