from neo4j import GraphDatabase
from db_config import neo4j_config
from src.services.search_services import get_property_owner_by_propertyId, get_property_with_adjacents, get_properties_by_ownerId, count_same_elements, update_property_owner, verify_neighbors_owner, get_owners
from src.services.area_services import get_property_area

#Responsável por fazer trocas de terrenos caso esta seja benéfica a nível de aumento de vizinho para ambos os proprietários
#Testar Dono 1 -> 4385    Dono 96 -> 4084
def trade_owners_properties(property1_id, property2_id):
    if property1_id == property2_id: return False

    property1_owner = get_property_owner_by_propertyId(property1_id)['owner_id']
    property2_owner = get_property_owner_by_propertyId(property2_id)['owner_id']
    print(property1_owner, property2_owner)
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
    
#Método que dado dois owners sugere possíveis trocas de terrenos que possam ocorrem
#Essas trocas levam em conta vizinhos pertencentes ao mesmo dono e ainda variações muito altas nas áreas
def suggestion_properties_trades(owner1_id,owner2_id):
    suggestions_list= []
    aux1_properties=[]
    aux2_properties=[]
    owner1_properties = get_properties_by_ownerId(owner1_id)['properties']
    owner2_properties = get_properties_by_ownerId(owner2_id)['properties']
    for property_owner1 in owner1_properties:
        property_owner1_neighbours = get_property_with_adjacents(property_owner1)['adjacent_properties']
        aux = list(set(property_owner1_neighbours) & set(owner2_properties))

        if len(aux) > 0 and verify_neighbors_owner(property_owner1,owner1_id):
            aux1_properties.append((owner1_id, property_owner1,get_property_area(property_owner1)['area']))
            for property_owner2 in aux:
                if verify_neighbors_owner(property_owner2,owner2_id):
                    aux2_properties.append((property_owner1, owner2_id, property_owner2, get_property_area(property_owner2)['area']))

    for property1 in aux1_properties:
        for property2 in aux2_properties:
            if property1[1] != property2[0] and abs(property1[2]-property2[3]) < 300:
                suggestions_list.append({
                    "owner1": {"owner1_id": property1[0], "property_id_owner1": property1[1]},
                    "owner2": {"owner2_id": property2[1], "property_id_owner2": property2[2]}
                })
    return suggestions_list

#Método que faz a sugestão de troca e ainda efetua as trocas
def suggestion_and_trade_properties(owner1_id, owner2_id):
    suggestions_list= suggestion_properties_trades(owner1_id,owner2_id)

    if(len(suggestions_list)==0): return False
    for suggestion in suggestions_list:
        owner1 = suggestion["owner1"]
        owner2 = suggestion["owner2"]

        owner1_id = owner1["owner1_id"]
        property_id_owner1 = owner1["property_id_owner1"]

        owner2_id = owner2["owner2_id"]
        property_id_owner2 = owner2["property_id_owner2"]

        update_property_owner(owner1_id,property_id_owner2)
        update_property_owner(owner2_id,property_id_owner1)

    return True



#Faz a comparação entre todos os owners para encontrar as melhores trocas
def get_suggestions_for_all_owner():
    all_owners = get_owners()
    suggestions_list = []
    for i, owner in enumerate(all_owners):
        for owner2 in all_owners[i + 1:]:
            a = suggestion_properties_trades(owner['owner_id'], owner2['owner_id'])
            print(f"Owner: {owner} Owner2: {owner2}")
            if len(a) > 0:
                suggestions_list.append(a)
    return suggestions_list

if __name__ == "__main__":
    #trade_owners_properties(4385,4084)
    print(suggestion_properties_trades(71,60))
    #suggestion_and_trade_properties(60,71)