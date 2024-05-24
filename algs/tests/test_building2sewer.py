from PyQt5.QtCore import *
from PyQt5.QtGui import *
from qgis.core import *
from qgis.gui import *
from qgis.utils import *

import processing

feedback = QgsProcessingFeedback()

nodes = QgsVectorLayer(
    'C:/Users/jpueyo/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/QGISprocessing/algs/dataset/buildings2sewer.gpkg|layername=nodes_with_sys_elev')
parcels = QgsVectorLayer(
    'C:/Users/jpueyo/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/QGISprocessing/algs/dataset/buildings2sewer.gpkg|layername=potable_connections')
dem = QgsRasterLayer(
    'C:/Users/jpueyo/AppData/Roaming/QGIS/QGIS3/profiles/default/python/plugins/QGISprocessing/algs/dataset/dem.tif')

if not nodes.isValid():
    raise TypeError("Nodes is not valid")
if not parcels.isValid():
    raise TypeError("Parcels is not valid")
if not dem.isValid():
    raise TypeError("DEM is not valid")

def test_building2sewer(params, text, feedback=None):
    print(text)
    output = processing.run('ICRA:buildings2sewer', params, feedback=feedback)

    if not output['OUTPUT'].isValid():
        raise TypeError("Output is None")
    if not output['LINES'].isValid():
        raise TypeError("Lines is None")

    print("Test passed")
    return None

params = {
    'INPUT': parcels,
    'INPUT_Z': '',
    'MANHOLES': nodes,
    'NODE_ID': 'node_id',
    'NODE_Z': 'sys_elev',
    'DEM': dem,
    'MAX_DIST': 100,
    'Z_TOL': 2,
    'OUTPUT': 'TEMPORARY_OUTPUT',
    'LINES_BOOL': True,
    'LINES': 'TEMPORARY_OUTPUT'
}

test_building2sewer(params, "Test 1: buildings2sewer with DEM and node_z and not input_z", feedback)

params['INPUT'] = nodes
params['DEM'] = None
params['INPUT_Z'] = 'sys_elev'
test_building2sewer(params, "Test 2: buildings2sewer without DEM and with node_z and not input_z", feedback)

params['INPUT'] = parcels
params['INPUT_Z'] = None
params['NODE_Z'] = None
params['DEM'] = dem
test_building2sewer(params, "Test 3: buildings2sewer with DEM and without node_z and input_z", feedback)

print("All tests passed")