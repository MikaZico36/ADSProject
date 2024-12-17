import geopandas as gpd
from shapely.geometry import shape
from werkzeug.utils import secure_filename
from geo_adjacency.adjacency import AdjacencyEngine
import os
import fiona
import json
import geojson
from neo4j import GraphDatabase
from db_config import neo4j_config
from concurrent.futures import ThreadPoolExecutor
from names_generator import generate_name
import random
import time


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


def get_features(file_path):
    with open(file_path) as f:
        data = geojson.load(f)
        features = data.get("features", [])
    return features


def create_properties(file_path):
    features = get_features(file_path)

    def process_batch(batch):
        driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
        with driver.session() as session:
            for feature in batch:
                object_id = feature['properties'].get('OBJECTID', None)
                shape_area = feature['properties'].get('Shape_Area', None)
                shape_length = feature['properties'].get('Shape_Length', None)
                multipolygon = str(feature['geometry'].get('coordinates', None))

                session.run(
                    """
                    MERGE (p:Property {object_id: $object_id})
                    SET p.shape_area = $shape_area,
                        p.shape_length = $shape_length,
                        p.multipolygon = $multipolygon
                    """,
                    object_id=object_id, shape_area=shape_area, shape_length=shape_length, multipolygon=multipolygon
                )
                print(f"Property created with object_id: {object_id}")
        driver.close()

    with ThreadPoolExecutor() as executor:
        batches = [features[i:i + 100] for i in range(0, len(features), 100)]
        futures = [executor.submit(process_batch, batch) for batch in batches]

        for future in futures:
            future.result()


def create_property_relationships(file_path):
    graph = create_relationship_dictionay(file_path)

    def process_batch(batch):
        driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
        with driver.session() as session:
            for node, neighbors in batch:
                for neighbor in neighbors:
                    existing_relationship = session.run(
                        """
                        MATCH (a:Property {object_id: $object_id})-[r:ADJACENT_TO]-(b:Property {object_id: $neighbor_object_id})
                        RETURN r
                        """,
                        object_id=node, neighbor_object_id=neighbor
                    ).single()

                    if not existing_relationship:
                        session.run(
                            """
                            MATCH (a:Property {object_id: $object_id}), (b:Property {object_id: $neighbor_object_id})
                            MERGE (a)-[:ADJACENT_TO]->(b)
                            """,
                            object_id=node, neighbor_object_id=neighbor
                        )
                        print(f"Relationship created between {node} and {neighbor}")
        driver.close()

    items = list(graph.items())
    with ThreadPoolExecutor() as executor:
        batches = [items[i:i + 100] for i in range(0, len(items), 100)]
        futures = [executor.submit(process_batch, batch) for batch in batches]

        for future in futures:
            future.result()


def create_owners(number_owners):
    owners = [(idx + 1, generate_name()) for idx in range(number_owners)]

    def process_batch(batch):
        driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
        with driver.session() as session:
            for owner_id, name in batch:
                session.run(
                    "MERGE (o:Owner {owner_id: $owner_id}) SET o.name = $name",
                    owner_id=owner_id, name=name
                )
                print(f"Owner created with owner_id: {owner_id}, and name: {name}")
        driver.close()


    batches = [owners[i:i + 50] for i in range(0, len(owners), 50)]
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_batch, batch) for batch in batches]
        
        for future in futures:
            future.result()

def generate_owner_distribution(num_owners):
    values = [random.random() for _ in range(num_owners)]
    
    total = sum(values)
    normalized_values = [v / total for v in values]

    owners_values = {i: normalized_values[i] for i in range(num_owners)}

    return owners_values



def create_ownership_relationships(distribution):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))

    with driver.session() as session:
        owners_ids = session.run("MATCH (o:Owner) RETURN o.owner_id").value()
        owners_ids.sort()
        property_ids = session.run("MATCH (p:Property) RETURN p.object_id").value()
        random.shuffle(property_ids)
        
        def process_batch(batch):
            driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
            with driver.session() as session:
                for owner, properties in batch:
                    for property in properties:
                        session.run(
                            """
                            MATCH (o:Owner {owner_id: $owner_id}), (p:Property {object_id: $property_id})
                            MERGE (o)-[:OWNS]->(p)
                            """,
                            owner_id=owner, property_id=property
                        )
                        print(f"Relationship created between owner_id: {owner} and property_id: {property}")


        dictionary = {owner_id: [] for owner_id in owners_ids}

        if distribution == "uniform":
            for idx, property_id in enumerate(property_ids):
                owner_id = owners_ids[idx % len(owners_ids)]
                dictionary[owner_id].append(property_id)

        #Para esta distribuição, a ideia é que cada cliente escolha a distribuição que quer, mas apra fim de 
        # testes a função generate_owner_distribution vai fazer essa distribuição de forma aleatória
        elif distribution == "user_choice":
            total_properties = len(property_ids)
            values = generate_owner_distribution(len(owners_ids)) 

            distribution_counts = {owner_id + 1: int(values[owner_id] * total_properties) for owner_id in values}

            assigned_properties = sum(distribution_counts.values())

            remaining = total_properties - assigned_properties
            if remaining > 0:
                for owner_id in sorted(distribution_counts.keys()):
                    if remaining == 0:
                        break
                    distribution_counts[owner_id] += 1
                    remaining -= 1

            current_index = 0
            for owner_id, count in distribution_counts.items():
                dictionary[owner_id] = property_ids[current_index:current_index + count]
                current_index += count
        else:
            print("Invalid distribution type")
            return

        items = list(dictionary.items())
        batches = [items[i:i + 5] for i in range(0, len(items), 5)]
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_batch, batch) for batch in batches]
            for future in futures:
                future.result()

    driver.close()



if __name__ == "__main__":
    file_path = "src/data_files/input_files/Acores_Grupo_Ocidental_Parcelas_az_oc.geojson"

    start = time.time()

    create_properties(file_path)
    create_property_relationships(file_path)
    create_owners(100)
    create_ownership_relationships("uniform")

    end = time.time()
    print(f"Tempo total: {end - start}")