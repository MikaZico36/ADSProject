from xml.sax.handler import all_properties

from neo4j import GraphDatabase

from src.services.db_config import neo4j_config
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

def get_property_area(property_id):
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

#Calcula a área total de todos os terrenos de um determinado dono
def get_total_area_by_owner(owner_id):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    with driver.session() as session:
        result = session.run(
            """
            MATCH (o:Owner {owner_id: $owner_id})-[:OWNS]->(p:Property)
            RETURN sum(p.shape_area) AS total_area
            """,
            owner_id=owner_id
        ).single()

        driver.close()

        if result and result["total_area"] is not None:
            return result["total_area"]
        return None


def get_mean_area_by_owner(owner_id):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    with driver.session() as session:
        result = session.run(
            """
            MATCH (o:Owner {owner_id: $owner_id})-[:OWNS]->(p:Property)
            RETURN avg(p.shape_area) AS mean_area
            """,
            owner_id=owner_id
        ).single()

        driver.close()

        if result and result["mean_area"] is not None:
            return result["mean_area"]
        return None






#Calcula a área de uma propriedade
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
        print(total_area)

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

        total_property_areas = 1
        adjacent_property_areas = []
        
        adjacent = []
        while property_ids:   
            for property_id in property_ids:
                result = session.run(
                    """
                    MATCH (p:Property {object_id: $property_id})-[:ADJACENT_TO*0..]-(neighbor)
                    RETURN DISTINCT neighbor.object_id AS adjacent_properties

                    """,
                    property_id=property_id
                ).single()
                teste = [record["adjacent_properties"] for record in result]
                print(teste)
                property = result["adjacent_properties"]
                if property in property_ids:
                    adjacent.append(property)
            
            adjacent_property_areas.append((total_property_areas, calculate_total_area(adjacent)))
            total_property_areas =+ 1
            adjacent = []
                    
        driver.close()
        print(adjacent_property_areas)
        return adjacent_property_areas

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

#Responsável por fazer trocas de terrenos caso esta seja benéfica a nível de aumento de vizinho para ambos os proprietários
#Testar Dono 1 -> 4385    Dono 96 -> 4084

def trade_owners_properties(property1_id, property2_id):
    if property1_id == property2_id: return False

    property1_owner = get_property_owner_by_propertyId(property1_id)
    property2_owner = get_property_owner_by_propertyId(property2_id)
    if property1_owner == property2_owner:
        return False
    property1_neighbors = get_property_with_adjacents(property1_id)['adjacent_properties']
    property2_neighbors = get_property_with_adjacents(property2_id)['adjacent_properties']
    property1_owner_properties = get_properties_by_ownerId(property1_owner)
    property2_owner_properties = get_properties_by_ownerId(property2_owner)
    property1_area= get_property_area(property1_id)['area']
    property2_area = get_property_area(property2_id)['area']

    count_neighbors_for_property2_to_owner1 = count_same_elements(property2_neighbors, property1_owner_properties)
    count_neighbors_for_property1_to_owner1 = count_same_elements(property1_neighbors, property1_owner_properties)
    diff_between_neighbors1 = (count_neighbors_for_property2_to_owner1 - count_neighbors_for_property1_to_owner1)

    count_neighbors_for_property1_to_owner2 = count_same_elements(property1_neighbors, property2_owner_properties)
    count_neighbors_for_property2_to_owner2 = count_same_elements(property2_neighbors, property2_owner_properties)
    diff_between_neighbors2 = (count_neighbors_for_property1_to_owner2 - count_neighbors_for_property2_to_owner2)

    if diff_between_neighbors1 >= 0 and diff_between_neighbors2 >= 0 and abs(property1_area- property2_area) < 300:
        update_property_owner(property1_owner,property2_id)
        update_property_owner(property2_owner,property1_id)
        return True
    else:
        return False



if __name__ == "__main__":

    start = time.time()
    #print(get_property_area(4385))
    #print(get_property_with_adjacents(4385))
    #print(get_property_owner_by_propertyId(4084))
    #print(get_property_owner_by_propertyId(4786))
    #print(get_property_owner_by_propertyId(4787))
    update_property_owner(1,4385)
    update_property_owner(96,4084)

    #print(109)
    #print(get_property_area(109))
    #print(get_property_owner_by_propertyId(109))

    #print("Vamos ver as áreas")
    #teste(96,3800,4400)

    #print(trade_properties(4385,4084))
    end = time.time()
    print(f"Tempo total: {end - start}")
