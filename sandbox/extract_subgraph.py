import networkx as nx
import pickle

nodes = QgsVectorLayer(r'C:\Users\jpueyo\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGISprocessing\algs\dataset\AdG_node_2021.gpkg','nodes','ogr')
arcs = QgsVectorLayer(r'C:\Users\jpueyo\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGISprocessing\algs\dataset\AdG_arc_2021.gpkg','arcs','ogr')

node_id = 'node_id'
edar_code = '32377'

def update_changed_field(graph, node, list):
    changed = nx.get_node_attributes(graph, 'changed')
    if changed.get(node) is None:
        return list
    else:
        return changed[node] + list
    
if not nodes.isValid():
    print("Nodes is not valid")
if not arcs.isValid():
    print("Arcs is not valid")
    
G = nx.DiGraph()

G.add_nodes_from([(feat[node_id], feat.__geo_interface__["properties"]) for feat in nodes.getFeatures() if feat['state'] != 0])

G.add_edges_from([(feat['node_1'], feat['node_2'], feat.__geo_interface__["properties"]) for feat in arcs.getFeatures() if feat['state'] != 0])

def create_graph_request(G, element, id):

    if element == 'nodes':
        idx_list = list(G.nodes())
    elif element == 'edges':
        fids = nx.get_edge_attributes(G, id)
        idx_list = list(fids.values())
        print(idx_list)
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

print(create_graph_request(G, "edges", 'fid'))

stop()


print(f"nodes = {len(G.nodes)}")
print(f"arcs = {len(G.edges)}")

G_notDi = nx.Graph(G)
connected_to_wwtp = nx.node_connected_component(G_notDi, edar_code)
subGraph = G.subgraph(connected_to_wwtp)

# Set outfall attributes to wwtp node
changed = update_changed_field(subGraph, 'node', edar_code, ['epa_type', 'sys_type', 'node_type'])

new = 'OUTFALL'
nx.set_node_attributes(subGraph, 
    {edar_code : {'epa_type': new, 'sys_type': new, 'node_type': new , 
    'changed': changed}    
    })
    
print("changed_field", nx.get_node_attributes(subGraph, 'changed'))

# Create a request to filter the nodes that are in the subGraph
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

exp = "\"node_id\" IN (" + exp1 + ")" 

exp = QgsExpression(exp)
request = QgsFeatureRequest(exp)

changed = nx.get_node_attributes(subGraph, 'changed')

for feat in nodes.getFeatures(request):
    if changed.get(feat[node_id]) is not None:
        print('changed', feat[node_id])
        break


