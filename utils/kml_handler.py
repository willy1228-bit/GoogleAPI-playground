import re
import xml.etree.ElementTree as ET
import numpy as np
from math import radians, sin, cos, sqrt, atan2

def read_kml_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def parse_location(file_path, route_name='route1', num_points=None, step_distance=None):
    kml_data = read_kml_file(file_path)
    root = ET.fromstring(kml_data)
    namespace = {"kml": "http://www.opengis.net/kml/2.2"}
    placemark = root.find(f".//kml:Placemark[kml:name='{route_name}']", namespace)
    coordinates_text = placemark.find(".//kml:coordinates", namespace).text.strip()
    coordinates = [
        tuple(map(float, coord.split(',')[::-1][1:])) for coord in coordinates_text.split()
    ]
    
    # Apply advanced interpolation
    interpolated_coordinates = advanced_interpolate(coordinates, num_points, step_distance)
    
    return interpolated_coordinates

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    return R * c

def advanced_interpolate(coordinates, num_points=None, step_distance=None):
    # Convert the list of coordinates into arrays of latitude and longitude
    lats = np.array([coord[1] for coord in coordinates])
    lons = np.array([coord[0] for coord in coordinates])

    # Calculate distances between points in meters
    distances = np.array([haversine_distance(lats[i], lons[i], lats[i+1], lons[i+1]) 
                          for i in range(len(lats)-1)])
    cumulative_distances = np.insert(np.cumsum(distances), 0, 0)
    total_distance = cumulative_distances[-1]

    if step_distance is not None:
        num_points = int(total_distance / step_distance) + 1
        print(f"Using step_distance: {step_distance}m. Calculated {num_points} points.")
    elif num_points is None:
        raise ValueError("Either num_points or step_distance must be provided.")
    else:
        print(f"Using num_points: {num_points}")

    # Interpolation points
    interp_distances = np.linspace(0, total_distance, num_points)

    # Interpolated latitude and longitude values
    interp_lats = np.interp(interp_distances, cumulative_distances, lats)
    interp_lons = np.interp(interp_distances, cumulative_distances, lons)

    # Interpolated coordinates
    interpolated_coordinates = list(zip(interp_lons, interp_lats))

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