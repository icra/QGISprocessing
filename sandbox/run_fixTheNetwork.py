import processing

feedback = QgsProcessingFeedback()
params = {'ARCS' : 'C:/Users/jpueyo/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/QGISprocessing/algs/dataset/AdG_arc_2021.gpkg|layername=arc', 'FIXED_ARCS' : 'TEMPORARY_OUTPUT', 'FIXED_NODES' : 'TEMPORARY_OUTPUT', 'NODES' : 'C:/Users/jpueyo/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/QGISprocessing/algs/dataset/AdG_node_2021.gpkg|layername=node', 'node_1' : 'node_1', 'node_2' : 'node_2', 'node_id' : 'node_id', 'wwtp' : '32377' }

processing.runAndLoadResults('ICRA:fixTheNetwork', params, feedback=feedback)




