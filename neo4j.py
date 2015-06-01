__author__ = 'pasha'
import py2neo
from py2neo import Graph, Node, Relationship, authenticate
import json
import requests
authenticate("localhost:7474", "neo4j", "sharik987p123")


def get_objects(name):
    """
    fetches objects from my register

    name: method, author, category
    returns: dictionary
    """
    request = requests.get('http://127.0.0.1:5010/api/' + str(name))
    api_data = json.loads(request.text)
    #print(request.text)
    return api_data["objects"]

def get_object(name):
    """
    fetches objects from my register

    name: method, author, category
    returns: dictionary
    """
    request = requests.get('http://127.0.0.1:5010/api/' + str(name))
    api_object = json.loads(request.text)
    #print(request.text)
    return api_object

def get_objects2(name):
    """
    fetches objects from second register
    name: experts, documents, commission orders, legal_issues, expertises
    returns: dictionary
    """
    request = requests.get('http://polar-journey-8507.herokuapp.com/api/' + str(name))
    api_data = json.loads(request.text)
    return api_data


# categories = get_objects('category')
def import_api_data():
    """
    imports data from my register (method and all adjacent) into graph DB
    """

    graph = Graph()
    graph.delete_all()
    # Uncomment on the first run!
    # graph.schema.create_uniqueness_constraint("Method", "id")
    # graph.schema.create_uniqueness_constraint("Author", "id")
    # graph.schema.create_uniqueness_constraint("Category", "id")

    SFs = get_objects('SF')

    for api_SF in SFs:

        node_SF = graph.merge_one("SF", "id", api_SF["id"])
        node_SF["name"] = api_SF["name"]
        node_SF["regnumb"] = api_SF["regnumb"]
        node_SF["datereg"] = api_SF["datereg"]

        api_person = api_SF["Person"]
        node_person = graph.merge_one("Person", "id", api_person["id"])
        node_person["name"] = api_person["name"]
        node_person.push()
        graph.create_unique(Relationship(node_person, " ", node_SF))

        api_address = api_SF["Address"]
        node_address = graph.merge_one("Address", "id", api_address["id"])
        node_address["city"] = api_address["city"]
        node_address.push()
        graph.create_unique(Relationship(node_address, " ", node_SF))

        for api_filia in api_SF["Filias"]:
            node_filia = graph.merge_one("Filia", "id", api_filia["id"])
            node_filia["name"] = api_filia["name"]
            node_filia.push()
            graph.create_unique(Relationship(node_filia, " ", node_SF))

        node_SF.push()

def import_api2_data():
    """
    imports data from second register (experts and all adjacent)

    """
    graph = Graph()
    # Uncomment on first run!
    #graph.schema.create_uniqueness_constraint("Expert", "id")
    #graph.schema.create_uniqueness_constraint("Document", "id")
    #graph.schema.create_uniqueness_constraint("Comission_order", "id")
    #graph.schema.create_uniqueness_constraint("Legal_issue", "id")
    #graph.schema.create_uniqueness_constraint("Expertise", "id")

    experts = get_objects2("experts")

    for api_expert in experts:
        node_expert = graph.merge_one("Expert", "id", api_expert["id"])
        node_expert["name"] = api_expert["name"]
        node_expert["workplace"] = api_expert["workplace"]
        node_expert["address"] = api_expert["address"]
        node_expert["phone"] = api_expert["phone"]

        for api_document in api_expert["documents"]:
            node_document = graph.merge_one("Document", "id", api_document["id"])
            node_document["id_doc"] = api_document["id_doc"]
            node_document["release_date"] = api_document["release_date"]
            node_document["expiry_date"] = api_document["expiry_date"]
            node_document["document_type"] = api_document["document_type"]
            node_document.push()
            graph.create_unique(Relationship(node_expert, "SIGNED", node_document))

        for api_order in api_expert["commission_orders"]:
            node_order = graph.merge_one("Comission_order", "id", api_order["id"])
            node_order["commission_name"] = api_order["commission_name"]
            node_order["order_number"] = api_order["order_number"]
            node_order["order_date"] = api_order["order_date"]
            node_order.push()
            graph.create_unique(Relationship(node_order, "APPOINTED", node_expert))

            for api_expertise in api_order["expertises"]:
                node_expertise = graph.merge_one("Category", "id", api_expertise["id"])
                node_expertise["name"] = node_expertise["name"]
                node_expertise.push()
                graph.create_unique(Relationship(node_order, "INCLUDES", node_expertise))





        for api_issue in api_expert["legal_issues"]:
            node_issue = graph.merge_one("Legal_issue", "id", api_issue["id"])
            node_issue["description"] = api_issue["description"]
            node_issue["date"] = api_issue["date"]
            node_issue.push()
            graph.create_unique(Relationship(node_expert, "WORKED_ON", node_issue))



        node_expert.push()





if __name__ == "__main__":
    # graph = Graph()
    # graph.delete_all()
    import_api_data()
    # import_api2_data()
