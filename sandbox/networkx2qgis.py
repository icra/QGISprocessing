import networkx as nx
import processing

node_id = 'node_id'
edar_code = '32377'

G = nx.read_adjlist(r'C:\Users\jpueyo\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGISprocessing\algs\dataset\subGraph.adjlist')

nodes = QgsVectorLayer(r'C:\Users\jpueyo\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGISprocessing\algs\dataset\AdG_node_2021.gpkg','nodes','ogr')
#arcs = QgsVectorLayer(r'C:\Users\jpueyo\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\QGISprocessing\algs\dataset\AdG_arc_2021.gpkg','arcs','ogr')

# Creem una llista amb els id i les dades

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

#params = {'INPUT': nodes, 'EXPRESSION': exp, 'OUTPUT': 'memory:'}
#
#fixed_nodes = processing.run("native:extractbyexpression", params)['OUTPUT']

for feat in nodes.getFeatures(request):
    values = nodes_dict[feat[node_id]]
    print(values)
    new = QgsFeature(nodes.fields())
    new.setGeometry(feat.geometry())
    new.setAttributes(values)
    print(new['code'])
    break
    





