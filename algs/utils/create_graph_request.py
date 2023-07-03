from qgis.core import *

def create_graph_request(subGraph, node_id):

    nodes_dict = {}
    for node in subGraph.nodes(data = True):
        nodes_dict[node[0]] = node[1]
    nodes_list = list(nodes_dict.keys())

    exp1 = ''

    for node in nodes_list:
        exp1 = exp1 + "\'"
        exp1 = exp1 + node
        exp1 = exp1 + "\', "

    exp1 = exp1[:-2]

    exp = f"\"{node_id}\" IN (" + exp1 + ")"

    exp = QgsExpression(exp)
    return QgsFeatureRequest(exp)