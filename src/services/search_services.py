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

get_property_area(1)

def count_same_elements(properties_neighbors, properties_owner):
    count = sum(1 for item in properties_owner if item in properties_neighbors)
    return count


#TODO fazer a troca onde o terreno menor deve valorizar se tem vizinho e o terreno maior a área
#TODO Verificar se o terreno no sitio onde está não vai perder vizinhos
def trade_properties(property1_id, property2_id):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    with driver.session() as session:
        all_property1_neighbors = get_property_with_adjacents(property1_id)
        all_property2_neighbors = get_property_with_adjacents(property2_id)
        property1_area = get_property_area(property1_id)
        property2_area= get_property_area(property2_id)
        property1_owner = session.run(
            """
            MATCH (o:Owner)-[:OWNS]->(p:Property {object_id: $property1_id})
            RETURN o.owner_id AS owner_id, o.name AS owner_name
            """,
            property1_id=property1_id
        ).single()
        property2_owner = session.run(
            """
            MATCH (o:Owner)-[:OWNS]->(p:Property {object_id: $property2_id})
            RETURN o.owner_id AS owner_id, o.name AS owner_name
            """,
            property2_id=property2_id
        ).single()


        if property1_area > property2_area:

            property1_owner_name = property1_owner['owner_name']
            all_properties = get_owner_with_properties_by_name(property1_owner_name)

            number_of_properties_in_commun = count_same_elements(all_property2_neighbors['adjacent_properties'], all_properties['properties'])
            owner1_points = number_of_properties_in_commun * 100
            properties_area_diff = get_property_area(property1_id)['area'] - get_property_area(property2_id)['area']
            print(f"Diferenca de área: {properties_area_diff} | número de vizinhos ganhos: {number_of_properties_in_commun}")
            if owner1_points >= 100 and properties_area_diff >= 100:
                driver.close()
                return True
            driver.close()
            return False

        elif property2_area > property1_area:
            property2_owner_name = property2_owner['owner_name']
            all_properties = get_owner_with_properties_by_name(property2_owner_name)

            number_of_properties_in_commun = count_same_elements(all_property1_neighbors['adjacent_properties'],
                                                                 all_properties['properties'])
            owner2_points = number_of_properties_in_commun * 100
            properties_area_diff = get_property_area(property2_id)['area'] - get_property_area(property1_id)['area']
            print(f"Diferenca de área: {properties_area_diff} | número de vizinhos ganhos: {number_of_properties_in_commun}")

            if owner2_points >= 100 and properties_area_diff >= 100:
                driver.close()
                return True
            driver.close()
            return False







if __name__ == "__main__":

    start = time.time()
    
    #get_area_adject_properties_by_owner(1)
    #get_total_area_by_owner(2)
    a = get_property_with_adjacents(14)
    print(a)
    #trade_properties(1,14)
    print(get_owner_with_properties_by_name('trusting_rhodes'))
    area1 = get_property_area(14)
    area2 = get_property_area(411)
    print("Area1: " + str(area1))
    print("Area2: " + str(area2))
    a = trade_properties(14,411)
    print("Trade properties: " + str(a))
    end = time.time()
    print(f"Tempo total: {end - start}")
