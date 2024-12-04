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
from neo4j import GraphDatabase


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
        if "Parcelas" in layername:
            print(f"Layer: {layername}")
            gdf = gpd.read_file(file_path, layer=layername)
            json_path = os.path.join(upload_folder, f"{os.path.splitext(filename)[0]}_{layername}.geojson")
            gdf.to_file(json_path, driver="GeoJSON")
            json_files.append(json_path)

    os.remove(file_path)
    return json_files
  
    
def create_relationship_dictionay(file_path):
    with open(file_path) as f:
        source_geoms = [shape(feature["geometry"]) for feature in json.load(f)["features"]]

    engine = AdjacencyEngine(source_geoms, **{"max_distance": 100})
    adjacency_dict = engine.get_adjacency_dict()
    return adjacency_dict

def get_all_features(file_path):
    with open(file_path) as f:
        data = geojson.load(f)
        return data.get('features', [])

def count_features(file_path):
    with open(file_path) as f:
        data = geojson.load(f)
        return len(data['features'])


def create_graph_with_features(graph, features):
    uri = "bolt://44.204.212.169:7687"  
    username = "neo4j"
    password = "merchandise-yolks-telecommunication"
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        for node, neighbors in graph.items():
            feature = features[int(node)]  
            properties = feature['properties']
            geometry = feature['geometry']

            object_id = properties.get('OBJECTID', None)
            shape_area = properties.get('Shape_Area', None)
            shape_length = properties.get('Shape_Length', None)
            multipolygon = geometry.get('coordinates', None)

            session.run("""
                MERGE (n:Node {name: $node})
                SET n.object_id = $object_id,
                    n.shape_area = $shape_area,
                    n.shape_length = $shape_length,
                    n.multipolygon = $multipolygon
            """, node=node, object_id=object_id, shape_area=shape_area,
                shape_length=shape_length, multipolygon=str(multipolygon))

            for neighbor in neighbors:
                session.run("""
                    MATCH (a:Node {name: $node}), (b:Node {name: $neighbor})
                    MERGE (a)-[:CONNECTED_TO]->(b)
                """, node=node, neighbor=str(neighbor))

    driver.close()
    print("Graph created successfully")


def main():
    file_path = "data_files/input_files/Acores_Grupo_Ocidental_Parcelas_az_oc.geojson"
    dictionary = create_relationship_dictionay(file_path)
    print(dictionary)
    features = get_all_features(file_path)
    print(features)
    create_graph_with_features(dictionary, features)

if __name__ == "__main__":
    main()
