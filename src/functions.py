import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import MultiPolygon, shape
from shapely.wkt import loads
from werkzeug.utils import secure_filename
from geo_adjacency.adjacency import AdjacencyEngine
import os
import fiona
import json
import geojson

def save_file(file, upload_folder):
    filename = secure_filename(file.filename)
    
    if not filename.lower().endswith('.gpkg') or filename.lower().endswith('.xml'):
        return "Invalid file type. Only .gpkg or .xml files are allowed.", 400
    
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
    
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)  
    
    json_files = []
    for layername in fiona.listlayers(file_path):
        print(f"Layer: {layername}")
        gdf = gpd.read_file(file_path, layer=layername)
        json_path = os.path.join(upload_folder, f"{os.path.splitext(filename)[0]}_{layername}.geojson")
        gdf.to_file(json_path, driver="GeoJSON")
        json_files.append(json_path)

    os.remove(file_path)
    return json_files
    

def load_geojson(path):
    with open(path) as f:
        return [shape(feature["geometry"]) for feature in json.load(f)["features"]]


def main():
    source_geoms = load_geojson("data_files/input_files/Acores_Grupo_Ocidental_Parcelas_az_oc.geojson")
    engine = AdjacencyEngine(source_geoms, **{"max_distance": 100})
    adjacency_dict = engine.get_adjacency_dict()
    print(adjacency_dict)
    engine.plot_adjacency_dict()

if __name__ == "__main__":
    main()
