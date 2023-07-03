import networkx as nx

nodes = QgsVectorLayer(r'C:\Users\jpueyo\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGISprocessing\algs\dataset\AdG_node_2021.gpkg','nodes','ogr')
arcs = QgsVectorLayer(r'C:\Users\jpueyo\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGISprocessing\algs\dataset\AdG_arc_2021.gpkg','arcs','ogr')

node_id = 'node_id'
edar_code = '32377'


if not nodes.isValid():
    print("Nodes is not valid")
if not arcs.isValid():
    print("Arcs is not valid")
    
G = nx.DiGraph()

G.add_nodes_from([(feat[node_id], feat.__geo_interface__["properties"]) for feat in nodes.getFeatures() if feat['state'] != 0])

G.add_edges_from([(feat['node_1'], feat['node_2'], feat.__geo_interface__["properties"]) for feat in arcs.getFeatures() if feat['state'] != 0])

print(f"nodes = {len(G.nodes)}")
print(f"arcs = {len(G.edges)}")

G_notDi = nx.Graph(G)
connected_to_wwtp = nx.node_connected_component(G_notDi, edar_code)
subGraph = G.subgraph(connected_to_wwtp)

# Set outfall attributes to wwtp node
new = 'OUTFALL'
nx.set_node_attributes(subGraph, {edar_code : {'epa_type': new, 'sys_type': new, 'node_type': new }})

print(f'The operational network connected to WWTP ({edar_code}) contains: ')
print(f"nodes =  {len(subGraph.nodes)}")
print(f"edges = {len(subGraph.edges)}")

nx.write_adjlist(subGraph, r'C:\Users\jpueyo\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGISprocessing\algs\dataset\subGraph.adjlist')