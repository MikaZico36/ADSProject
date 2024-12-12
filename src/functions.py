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
import mysql.connector
from db_config import sql_config, neo4j_config
import numpy as np
from concurrent.futures import ThreadPoolExecutor


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
    print("criado")
    return adjacency_dict

def create_graph_in_neo4j(batch, graph):
    uri = neo4j_config["uri"]
    username = neo4j_config["username"]
    password = neo4j_config["password"]

    driver = GraphDatabase.driver(uri, auth=(username, password))
    with driver.session() as session:
        for node in batch:
            print(f"Processing node {node}")
            session.run("MERGE (:Node {id: $node})", node=node)
            for neighbor in graph[node]:
                session.run("""
                    MATCH (a:Node {id: $node}), (b:Node {id: $neighbor})
                    MERGE (a)-[:CONNECTED_TO]->(b)
                """, node=node, neighbor=neighbor)
    driver.close()

def create_thread_pool(graph):
    nodes = list(graph.keys())
    batch_size = 100

    batches = [nodes[i:i + batch_size] for i in range(0, len(nodes), batch_size)]

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(create_graph_in_neo4j, batch, graph) for batch in batches]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Erro ao processar um lote: {e}")


def get_features(file_path):
    with open(file_path) as f:
        data = geojson.load(f)
        features = data.get("features", [])
    return features


def create_database_and_table():
    conn = mysql.connector.connect(**sql_config)
    cursor = conn.cursor()

    cursor.execute("CREATE DATABASE IF NOT EXISTS ads")
    cursor.execute("USE ads")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS features (
            id INT AUTO_INCREMENT PRIMARY KEY,
            shape_length FLOAT,
            shape_area FLOAT,
            geometry JSON,
            node_id INT
        )
    ''')
    conn.commit()
    conn.close()

def insert_features(features):
    conn = mysql.connector.connect(**sql_config)
    cursor = conn.cursor()
    cursor.execute("USE ads")

    cursor.execute("TRUNCATE TABLE features")
    
    for feature in features:

        properties = feature.get("properties", {})
        geometry = feature.get("geometry", {})

        shape_length = properties.get("Shape_Length")
        shape_area = properties.get("Shape_Area")

        insert_stm = ("INSERT INTO features (shape_length, shape_area, geometry) VALUES (%s, %s, %s)")
        data = (shape_length, shape_area, json.dumps(geometry))

        cursor.execute(insert_stm, data)
    
    cursor.execute("UPDATE features SET node_id = id - 1")
    
    conn.commit()
    cursor.close()
    conn.close()

def process_geojson_to_sql(file_path):
    features = get_features(file_path)
    create_database_and_table()
    insert_features(features)

def main():
    file_path = "src/data_files/input_files/Acores_Grupo_Ocidental_Parcelas_az_oc.geojson"
    process_geojson_to_sql(file_path)

    #graph = create_relationship_dictionay(file_path)
    #create_thread_pool(graph)
    


if __name__ == "__main__":
    main()
