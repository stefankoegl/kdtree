import kdtree
from geopy import geocoders
from math import radians, cos, sin, asin, sqrt
import distance

g = geocoders.GoogleV3()

class Point:    
    def __init__(self, addressString=None, lat=None, lon=None):
        if lat != None and lon != None:
            self.address = addressString
            self.deg_lat = lat
            self.deg_lon = lon
        else: 
            self.address, (self.deg_lat, self.deg_lon) = g.geocode(addressString);
        
        self.convert_to_cartesian()
        self.data = (self.x, self.y, self.z)
        #self.data = (self.deg_lat, self.deg_lon)
    
    def __getitem__(self, key):
        return self.data[key]
    
    def __len__(self):
        return len(self.data)
        
    def distance(self, otherPoint):
        # Haversine does the conversion to radians.
        return distance.haversine([self.deg_lat, self.deg_lon], [otherPoint.deg_lat, otherPoint.deg_lon])
    
    def __str__(self):
        #return str(self.address[0:8]) + " " + str(self.x) + " " + str(self.y) + " " + str(self.z)
        return str(self.address[0:8]) + " " + str(self.deg_lat)[0:5] + " " + str(self.deg_lon)[0:5]
    
    #def to_point(self):
    #    return (self.lat, self.lon)
    
    def convert_to_cartesian(self):
        R = 6371
        self.rad_lat = radians(self.deg_lat)
        self.rad_lon = radians(self.deg_lon)
        self.x = R * cos(self.rad_lat) * cos(self.rad_lon)
        self.y = R * cos(self.rad_lat) * sin(self.rad_lon)
        self.z = R * sin(self.rad_lat)
        
    def __repr__(self):
        return self.address

class my_kd_tree:
    points_array = []
    
    def create_kd_tree(self):
        self.tree = kdtree.create(self.points_array)
        kdtree.visualize(self.tree)
        #point1 = (2, 3)
        #point2 = (7, 8)
        #tree = kdtree.create([point1, point2, point3])
    
    def k_nearest_neighbors(self, point, k):
        # The distance function is cartesian distance (we converted the points with this).
        neighbors = self.tree.search_knn(point, k)
        for neighbor in neighbors:
            print str(neighbor) + " " + str(neighbor[0].data.distance(point))
    
    def create_points(self):
        self.add_point_beginning("Miriam Haheshmonait 14 Tel Aviv")
        self.add_point_beginning("San Francisco")
        self.add_point_beginning("Rabin Square Tel Aviv")
        self.add_point_beginning("New York")
        self.add_point_beginning("Caracas")
        self.add_point_beginning("Argentina")
        self.add_point_beginning("Cuzco Peru")
        self.add_point_beginning("Shangai China")
        self.add_point_beginning("Eastern Russia", 66.593382, 179.924234)
        self.add_point_beginning("Eastern 2", 67.885175, -176.823813)        

        #self.addPoint("Dizengoff 125 Tel Aviv")
        #self.addPoint("Ussishkin 42 Jerusalem")
        #self.addPoint("14 rue Bremontier 75017 Paris")
        #self.addPoint("Bograshov 14 Tel Aviv")
                
    def add_point_beginning(self, address, lat=None, lon=None):
        self.points_array.append(Point(address, lat, lon))
        
    def add_point_dynamic(self, address, lat=None, lon=None):
        self.tree.add()
    
    def print_points(self):
        for point in self.points_array:
            print point
            
if __name__ == "__main__":
    test = my_kd_tree()
    test.create_points()
    test.print_points()
    test.create_kd_tree()
    
    test_point = Point("Bastille paris")
    print test_point
    #print testPoint.distance(ny);
    test.k_nearest_neighbors(test_point, 15)