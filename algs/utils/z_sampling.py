from qgis.PyQt.QtCore import *
from qgis.core import *
def z_sampling(points, mde, feedback, z_field='z'):

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
    if mem_layer.fields().indexFromName(z_field) == -1:
        z = QgsField(z_field, QVariant.Double)
        mem_layer.dataProvider().addAttributes([z])
        mem_layer.updateFields()

    #search the index of z field
    idx = mem_layer.fields().indexFromName(z_field)

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