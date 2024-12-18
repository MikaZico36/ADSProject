from neo4j import GraphDatabase
from db_config import neo4j_config
from services.search_services import check_neighbors

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

        pairs = check_neighbors(property_ids)
        
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
    

#permite que o user escolha propriedades vizinhas e veja a area total dessas propriedades
def get_selected_subarea(properties_ids):
    driver = GraphDatabase.driver(neo4j_config["uri"], auth=(neo4j_config["username"], neo4j_config["password"]))
    with driver.session() as session:
        result = session.run(
            """
            WITH $properties_ids AS property_ids  
            MATCH (p:Property)
            WHERE p.object_id IN property_ids
            RETURN SUM(p.shape_area) AS total_area
            """,
            properties_ids=properties_ids).single()

        driver.close()
        return result['total_area']
