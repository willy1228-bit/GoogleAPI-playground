# Import google_streetview for the api module
import google_streetview.api
from dotenv import load_dotenv
import os
import argparse
import math

from utils.kml_handler import parse_location

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment variable
api_key = os.getenv('GOOGLE_API_KEY')


def create_params(location, heading):
    base_params = {
        'size': '600x300',
        'pitch': '0',
        'key': api_key
    }
    if isinstance(location, list):
        return [{**base_params, 'location': f"{loc[0]}, {loc[1]}", 'heading': str(h)} for loc, h in zip(location, heading)]

    return [{**base_params, 'location': f"{location[0]}, {location[1]}", 'heading': str(h)} for h in heading]


def get_street_view_images(params, save_folder='downloads'):
    results = google_streetview.api.results(params)
    results.download_links(save_folder)
    results.save_links('links.txt')
    results.save_metadata('metadata.json')

def calculate_heading(coord1, coord2, angle_offset=0):
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    delta_lon = lon2 - lon1
    x = math.sin(math.radians(delta_lon)) * math.cos(math.radians(lat2))
    y = (math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) -
         (math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(math.radians(delta_lon))))
    heading = math.atan2(x, y)
    return (math.degrees(heading) + 360 + angle_offset) % 360


def process_kml_file(file_path, filename, raw_data_path):
    if os.path.exists(file_path):
        os.system(f'mv {os.path.join(raw_data_path, filename + ".kmz")} {os.path.join(raw_data_path, filename + ".zip")}')
        if os.path.exists(os.path.join(raw_data_path, filename + ".zip")):
            os.system(f'unzip {os.path.join(raw_data_path, filename + ".zip")} -d {os.path.join(raw_data_path, filename)}')
            os.system(f'rm {os.path.join(raw_data_path, filename + ".zip")}')


def main(args):
    filename = os.path.basename(args.file_path).split(".")[0]
    process_kml_file(args.file_path, filename, args.raw_data_path)

    location = parse_location(os.path.join(args.raw_data_path, filename, "doc.kml"), route_name=args.route_name, num_points=args.num_points)
    headings = [int(calculate_heading(location[i], location[i + 1], args.angle)) for i in range(len(location) - 1)]
    headings.append(headings[-1])

    params = create_params(location, headings)
    save_folder = args.save_folder
    get_street_view_images(params, save_folder=save_folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # add raw file path
    # add route name
    # add number of points to interpolate
    # add heading
    parser.add_argument('-f', '--file_path', type=str, help='Path to the kml file')
    parser.add_argument('-r', '--route_name', type=str, help='Name of the route')
    parser.add_argument('-n', '--num_points', type=int, help='Number of points to interpolate')
    parser.add_argument('-H', '--heading', type=list, default=[180], help='Heading of the street view image')
    parser.add_argument('-s', '--save_folder', type=str, help='Folder to save the street view images')
    parser.add_argument('-a', '--angle', type=int, default=0, help='Angle offset from the forward direction (0-359 degrees)')
    parser.add_argument('-d', '--raw_data_path', type=str, default='maps_raw_data', help='Path to the raw data directory')
    args = parser.parse_args()
    main(args)