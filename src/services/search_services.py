from neo4j import GraphDatabase
from db_config import neo4j_config
import time

def get_owner_by_id(owner_id):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))

    with driver.session() as session:
        owner = session.run(
            "MATCH (o:Owner {owner_id: $owner_id}) RETURN o.owner_id, o.name",
            owner_id=owner_id
        ).single()
    driver.close()

    return owner

def get_owner_by_name(name):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))

    with driver.session() as session:
        owner = session.run(
            "MATCH (o:Owner {name: $name}) RETURN o.owner_id, o.name",
            name=name
        ).single()
    driver.close()

    return owner


def get_owners():
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))

    with driver.session() as session:
        owners = session.run("MATCH (o:Owner) RETURN o.owner_id, o.name").data()
    driver.close()
    
    return owners

def get_owner_with_properties_by_name(name):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))

    with driver.session() as session:
        result = session.run(
            """
            MATCH (o:Owner {name: $name})-[:OWNS]->(p:Property)
            RETURN o.owner_id AS owner_id, o.name AS owner_name, collect(p.object_id) AS properties
            """,
            name=name
        ).single()

    driver.close()

    if result:
        return {
            "owner_id": result["owner_id"],
            "owner_name": result["owner_name"],
            "properties": result["properties"]
        }
    else:
        return None

def get_property_with_adjacents(property_id):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))

    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Property {object_id: $property_id})
            OPTIONAL MATCH (p)-[:ADJACENT_TO]-(adjacent:Property)
            RETURN p.object_id AS property_id, 
                   p.name AS property_name, 
                   collect(adjacent.object_id) AS adjacent_properties
            """,
            property_id=property_id
        ).single()

    driver.close()

    if result:
        return {
            "property_id": result["property_id"],
            "property_name": result["property_name"],
            "adjacent_properties": result["adjacent_properties"]
        }
    else:
        return None

def get_propertie_area(property_id):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    with driver.session() as session:
        area = session.run(
            """
            MATCH (p:Property {object_id: $property_id})
            RETURN p.shape_area AS area
            """,
            property_id=property_id
        ).single()
        driver.close()
        return area

def get_total_area_by_owner(owner_id):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    with driver.session() as session:
        total_area = session.run("""

            MATCH (o:Owner {owner_id: $owner_id})-[:OWNS]->(p:Property)
                             RETURN sum(p.shape_area) AS total_area
            """, 
            owner_id=owner_id).single()
        driver.close()
        print(total_area)
        return total_area
    
def calculate_total_area(property_ids):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    
    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Property)
            WHERE p.object_id IN $property_ids
            RETURN sum(p.shape_area) AS total_area
            """,
            property_ids=property_ids
        ).single()
        
        total_area = result["total_area"] if result and result["total_area"] else 0.0
    
    driver.close()
    return total_area
        
def get_area_adject_properties_by_owner(owner_id):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    with driver.session() as session:
        result = session.run(
            """
            MATCH (o:Owner {owner_id: $owner_id})-[:OWNS]->(p:Property)
            RETURN collect(p.object_id) AS property_ids
            """,
            owner_id=owner_id
        ).single()

        property_ids = result["property_ids"]

        result = session.run(
                """
                UNWIND $property_ids AS prop_id
                MATCH (p1:Property {object_id: prop_id})-[:ADJACENT_TO]-(p2:Property)
                WHERE p2.object_id IN $property_ids
                RETURN DISTINCT p1.object_id AS property_id_1, p2.object_id AS property_id_2
                """,
                property_ids=property_ids
            )
        pairs = set(tuple(sorted((record["property_id_1"], record["property_id_2"]))) for record in result)
        driver.close()
        
        index = 1
        adjacent_property_areas = []

        for pair in pairs:
            total_area = calculate_total_area(list(pair))
            adjacent_property_areas.append({"subarea_id": index, "area": total_area})
            index += 1
            property_ids.remove(pair[0])
            property_ids.remove(pair[1])

        for property_id in property_ids:
            total_area = calculate_total_area([property_id])
            adjacent_property_areas.append({"subarea_id": index, "area": total_area})
            index += 1
        
        return adjacent_property_areas
                
if __name__ == "__main__":

    start = time.time()
    
    get_area_adject_properties_by_owner(1)

    end = time.time()
    print(f"Tempo total: {end - start}")
