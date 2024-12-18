from xml.sax.handler import all_properties

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
        owners = session.run("MATCH (o:Owner) RETURN o.owner_id AS owner_id, o.name AS owner_name").data()
    driver.close()

    return owners

def get_properties():
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))

    with driver.session() as session:
        properties = session.run("MATCH (p:Property) RETURN p.object_id AS property_id, p.shape_area AS area").data()
    driver.close()

    return properties


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

def check_neighbors(properties):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    with driver.session() as session:
        result = session.run(
            """
            UNWIND $properties AS prop_id
            MATCH (p1:Property {object_id: prop_id})-[:ADJACENT_TO]-(p2:Property)
            WHERE p2.object_id IN $properties
            RETURN DISTINCT p1.object_id AS property_id_1, p2.object_id AS property_id_2
            """,
            properties=properties
        )
        pairs = set(tuple(sorted((record["property_id_1"], record["property_id_2"]))) for record in result)
        driver.close()
        return pairs



#Conta os elementos em comum em duas listas
def count_same_elements(properties_neighbors, properties_owner):
    count = sum(1 for item in properties_owner if item in properties_neighbors)
    return count

#Retorna o Owner_Id com base no id de uma propriedade
def get_property_owner_by_propertyId(propertyId):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    with driver.session() as session:
        property1_owner = session.run(
            """
            MATCH (o:Owner)-[:OWNS]->(p:Property {object_id: $propertyId})
            RETURN o.owner_id AS owner_id, o.name AS owner_name
            """,
            propertyId=propertyId
        ).single()
    driver.close()
    return property1_owner['owner_id']

#Através do Id do owner devolve a lista de todas as suas propriedades
def get_properties_by_ownerId(ownerId):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    with driver.session() as session:
        result = session.run(
            """
            MATCH (o:Owner {owner_id: $ownerId})-[:OWNS]->(p:Property)
            RETURN o.owner_id AS owner_id, o.name AS owner_name, collect(p.object_id) AS properties
            """,
            ownerId=ownerId
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


#Altera o dono de uma propriedade
def update_property_owner(new_owner_id,property_id):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))

    with driver.session() as session:
        session.run(
            """
            MATCH (p:Property {object_id: $property_id})<-[r:OWNS]-(current_owner:Owner)
            MATCH (new_owner:Owner {owner_id: $new_owner_id})
            DELETE r
            CREATE (new_owner)-[:OWNS]->(p)
            """,
            property_id=property_id,
            new_owner_id=new_owner_id
        )

    driver.close()
    return {"property_id": property_id, "new_owner_id": new_owner_id}


def verify_neighbors_owner(property_id, owner_id):
    property1_neighbors = get_property_with_adjacents(property_id)['adjacent_properties']

    for property in property1_neighbors:
        owner_property_id = get_property_owner_by_propertyId(property)
        if owner_property_id == owner_id:
            return False

    return True

if __name__ == "__main__":

    start = time.time()
    #print(get_property_area(4385))
    #print(get_property_with_adjacents(4385))
    #print(get_property_owner_by_propertyId(4084))
    #print(get_property_owner_by_propertyId(4786))
    #print(get_property_owner_by_propertyId(4787))
    #update_property_owner(1,4385)
    #update_property_owner(96,4084)

    #print(109)
    #print(get_property_area(109))
    #print(get_property_owner_by_propertyId(109))

    #print("Vamos ver as áreas")
    #teste(96,3800,4400)
    
    #get_selected_subarea([4385,4084])
    #trades_to_maximaze_total_area(1)

    #print(suggestion_properties_trades(1,51))

    #print(trade_properties(4385,4084))
    #get_suggestions_for_all_owner()

    end = time.time()
    print(f"Tempo total: {end - start}")
