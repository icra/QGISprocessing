from qgis.PyQt.QtCore import *
from PyQt5.QtGui import QIcon
from qgis.core import *
import qgis.utils
import processing

def checkExtent(layer, background):
    xMaxL = layer.extent().xMaximum()
    xMinL = layer.extent().xMinimum()
    yMaxL = layer.extent().yMaximum()
    yMinL = layer.extent().yMinimum()

    xMaxB = background.extent().xMaximum()
    xMinB = background.extent().xMinimum()
    yMaxB = background.extent().yMaximum()
    yMinB = background.extent().yMinimum()

    if xMaxL > xMaxB or xMinL < xMinB or yMaxL > yMaxB or yMinL < yMinB:
        return False
    else:
        return True

def z_sampling(points, mde, feedback):

    #create z field if it don't exist
    if points.fields().indexFromName('z') == -1:
        z = QgsField('z', QVariant.Double)
        points.dataProvider().addAttributes([z])
        points.updateFields()

    #search the index of z field
    idx = points.fields().indexFromName('z')

    #set the progressbar
    total = 100.0 / points.featureCount() if points.featureCount() else 0
    features = points.getFeatures()

    mem_layer = QgsVectorLayer("Point", "duplicated_layer", "memory")

    mem_layer_data = mem_layer.dataProvider()
    attr = points.dataProvider().fields().toList()
    mem_layer_data.addAttributes(attr)
    mem_layer.updateFields()
    mem_layer_data.addFeatures(features)

    features = mem_layer.getFeatures()

    #open editing mode in points and write z values in z field
    with edit(mem_layer):
        for current, point in enumerate(features):
            if feedback.isCanceled():
                break

            x = point.geometry().asPoint()
            val, res = mde.dataProvider().sample(x, 1)
            point[idx] = val
            mem_layer.updateFeature(point)

            #update progressbar
            feedback.setProgress(int(current * total))
    return mem_layer
