import re
import xml.etree.ElementTree as ET
import numpy as np

def read_kml_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def parse_location(file_path, route_name='route1', num_points=20):
    kml_data = read_kml_file(file_path)
    root = ET.fromstring(kml_data)
    namespace = {"kml": "http://www.opengis.net/kml/2.2"}
    placemark = root.find(f".//kml:Placemark[kml:name='{route_name}']", namespace)
    coordinates_text = placemark.find(".//kml:coordinates", namespace).text.strip()
    
    coordinates = [
        tuple(map(float, coord.split(',')[::-1][1:])) for coord in coordinates_text.split()
    ]
    
    # Apply advanced interpolation
    interpolated_coordinates = advanced_interpolate(coordinates, num_points)
    
    return interpolated_coordinates

def advanced_interpolate(coordinates, num_points=20):

    # Convert the list of coordinates into arrays of x (longitude) and y (latitude)
    x = np.array([coord[0] for coord in coordinates])
    y = np.array([coord[1] for coord in coordinates])

    # Calculate the cumulative distances between each point
    distances = np.sqrt(np.diff(x)**2 + np.diff(y)**2)
    cumulative_distances = np.insert(np.cumsum(distances), 0, 0)

    # Interpolation points (20 points including the start and end points)
    interp_distances = np.linspace(0, cumulative_distances[-1], num_points)

    # Interpolated x and y values
    interp_x = np.interp(interp_distances, cumulative_distances, x)
    interp_y = np.interp(interp_distances, cumulative_distances, y)

    # Interpolated coordinates
    interpolated_coordinates = list(zip(interp_x, interp_y))

    # Print the interpolated coordinates
    for coord in interpolated_coordinates:
        print(f"{coord[0]},{coord[1]}")

    return interpolated_coordinates
    

if __name__ == '__main__':
    # Path to the KML file
    file_path = 'doc.kml'

    # Parse the location data
    # parse_location(file_path)

    # Original coordinates
    coordinates = [
        (120.9800618, 24.8033727),
        (120.9934514, 24.7989316),
        (120.9972708, 24.796633),
        (121.0046468, 24.7908702)
    ]
    advanced_interpolate(coordinates)