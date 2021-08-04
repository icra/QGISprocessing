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

    #set the progressbar
    total = 100.0 / points.featureCount() if points.featureCount() else 0
    features = points.getFeatures()

    mem_layer = QgsVectorLayer("Point", "duplicated_layer", "memory")

    mem_layer_data = mem_layer.dataProvider()
    attr = points.dataProvider().fields().toList()
    mem_layer_data.addAttributes(attr)
    mem_layer.updateFields()
    mem_layer_data.addFeatures(features)

    #create z field if it don't exist
    if mem_layer.fields().indexFromName('z') == -1:
        z = QgsField('z', QVariant.Double)
        mem_layer.dataProvider().addAttributes([z])
        mem_layer.updateFields()

    #search the index of z field
    idx = mem_layer.fields().indexFromName('z')

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
