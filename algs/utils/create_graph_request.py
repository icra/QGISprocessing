from qgis.core import *
import networkx as nx

def create_graph_request(G, element, id):
    '''
    G is the graph containing the nodes and edges that must be exported as spatial layer
    element is one of 'node' or 'edge' depending in which layer is being created
    id is the field used to filter the spatial layer used as input.
    '''

    if element == 'nodes':
        idx_list = list(G.nodes())
    elif element == 'edges':
        fids = nx.get_edge_attributes(G, id)
        idx_list = list(fids.values())
    else:
        raise Exception('elements must be one of nodes or edges')

    exp1 = ''

    for idx in idx_list:
        exp1 = exp1 + "\'"
        exp1 = exp1 + str(idx)
        exp1 = exp1 + "\', "

    exp1 = exp1[:-2]
    exp = f"\"{id}\" IN (" + exp1 + ")"

    exp = QgsExpression(exp)
    return QgsFeatureRequest(exp)