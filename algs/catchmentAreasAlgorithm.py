# -*- coding: utf-8 -*-

"""
/***************************************************************************
 buildings2sewert
                                 A QGIS plugin
 Connect buildings to the sewer system
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-06-15
        copyright            : (C) 2021 by Josep Pueyo-Ros, ICRA
        email                : jpueyo@icra.cat
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Josep Pueyo-Ros, ICRA'
__date__ = '2021-06-15'
__copyright__ = '(C) 2021 by Josep Pueyo-Ros, ICRA'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import *
from PyQt5.QtGui import QIcon
from qgis.core import *
import qgis.utils
import processing
import os

pluginPath = os.path.split(os.path.split(os.path.dirname(__file__))[0])[0]

class catchmentAreasAlgorithm(QgsProcessingAlgorithm):

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                'INPUT',
                self.tr('Outlets layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                'outlet_id',
                self.tr('Field with outlets id'),
                parentLayerParameterName='INPUT',
                allowMultiple=False
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                'DEM',
                self.tr('Filled elevations raster')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                'OUTPUT',
                self.tr('Output layer'),
                type = QgsProcessing.TypeVectorPolygon
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        input = self.parameterAsVectorLayer(parameters, 'INPUT', context)
        dem = self.parameterAsRasterLayer(parameters, 'DEM', context)
        outlet_id = self.parameterAsString(parameters, 'outlet_id', context)

        field = QgsFields()
        field.append(QgsField("id", QVariant.String))

        (sink, dest_id) = self.parameterAsSink(parameters, 'OUTPUT',
                context, field, QgsWkbTypes.Polygon, input.sourceCrs())

        total_points = input.featureCount()

        if input.fields().indexFromName('z') == -1:
            outlets = self.z_sampling(input, dem, feedback)
        else:
            outlets = input

        request = QgsFeatureRequest()

        # set order by field
        clause = request.OrderByClause('z', ascending=False)
        orderby = request.OrderBy([clause])
        request.setOrderBy(orderby)

        features = outlets.getFeatures(request)

        # Iterate over point features
        for i, pnt in enumerate(features):

            # if dem has been clipped use it as input_dem, otherwise use original dem
            if 'clip_dem' in locals():
                input_dem = clip_dem
                feedback.setProgressText('Using clipped dem')
            else:
                input_dem = dem

            # Get x and y coordinate from point feature
            geom = pnt.geometry()
            p = geom.asPoint()
            x = p.x()
            y = p.y()

            feedback.pushInfo('Creating upslope area for point ({}) - {} of {}'.format(
                pnt[outlet_id], i + 1, total_points))
            feedback.setProgress(i / total_points * 100)

            # Calculate catchment raster from point feature
            catchraster = processing.run("saga:upslopearea", {'TARGET':None,
                                        'TARGET_PT_X':x,
                                        'TARGET_PT_Y':y,
                                        'ELEVATION': input_dem,
                                        'SINKROUTE': None,
                                        'METHOD':0, 'CONVERGE':1.1,
                                        'AREA': 'TEMPORARY_OUTPUT'})
            # feedback.pushInfo('Catchment area created: ' + str(catchraster['AREA']))
            # Polygonize raster catchment
            catchpoly = processing.run("gdal:polygonize", {'INPUT':catchraster['AREA'],
                                        'BAND':1,
                                        'FIELD':'DN',
                                        'EIGHT_CONNECTEDNESS':False,
                                        'OUTPUT': 'TEMPORARY_OUTPUT'})

            # feedback.pushInfo('Catchment area polygonized: ' + str(catchpoly['OUTPUT']))
            # Select features having DN = 100 and export them to a SHP file
            catch_lyr = QgsVectorLayer(catchpoly['OUTPUT'], 'catchmments', 'ogr')
            exp = QgsExpression('"DN"=100')
            request = QgsFeatureRequest(exp)

            # add catchment area to output
            for feature in catch_lyr.getFeatures(request):
                sink.addFeature(feature, QgsFeatureSink.FastInsert)

            #create layer with polygon that is not catchment area
            catch_lyr.selectByExpression('"DN"<100')
            mask = processing.run("native:saveselectedfeatures", {'INPUT': catch_lyr, 'OUTPUT': 'memory'})['OUTPUT']
            catch_lyr.removeSelection()

            # delete catchment area from dem
            clip_output = processing.run("gdal:cliprasterbymasklayer", {
                                            'INPUT': input_dem,
                                            'MASK': mask,
                                            'SOURCE_CRS': input_dem.crs(),
                                            'TARGET_CRS': input_dem.crs(),
                                            'NODATA': null,
                                            'KEEP_RESOLUTION': True,
                                            'OUTPUT': 'C:/Users/Josep Pueyo-Ros/Desktop/plugin-test/clipped.sdat'})

            clip_dem = QgsRasterLayer(clip_output['OUTPUT'])

        return {'OUTPUT': dest_id}

    def name(self):

        return 'catchment areas'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    # def group(self):
    #     """
    #     Returns the name of the group this algorithm belongs to. This string
    #     should be localised.
    #     """
    #     return self.tr(self.groupId())
    #
    # def groupId(self):
    #     """
    #     Returns the unique ID of the group this algorithm belongs to. This
    #     string should be fixed for the algorithm, and must not be localised.
    #     The group id should be unique within each provider. Group id should
    #     contain lowercase alphanumeric characters only and no spaces or other
    #     formatting characters.
    #     """
    #     return 'Sewer system'

    def z_sampling(self, points, mde, feedback):
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

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'ICRA', 'icons', 'buildings2sewer.png'))

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return catchmentAreasAlgorithm()

    def shortHelpString(self):
        return "<p>This algorithm connects the buildings of a city to the manholes of the sewer system. It connects each building (using the centroid as a departure point) to the closest manhole that is in the same or in a lower altitude.</p>"\
        "<p>It returns the centroids of the buildings with the following fields:"\
        "<ul><li>Id of the manhole which the building is connected</li><li>Altitude of the building's centroid</li><li>Distance between the building's centroid and the connected manhole</li>"\
        "<li>Altitude difference between the building's centroid and the connected manhole</li></ul>"\
        "If \"Create connection lines is checked\", it also returns a layer with the lines showing each connection.</p>"\
        "<p>Two parameters can be adjusted:<ul>"\
        "<li> <b>Maximum distance:</b> If a connection is larger than the maximum distance, the algorithm searches manholes 1 meter above. This iteration is repeated until the connection is shorter than the maximum distance or until the altitude tolerance is reached </li>"\
        "<li> <b>Altitude tolerance:</b> It determines how many meters upper a manhole can be regarding the building to connect. The altitude tolerance is only used when the maximum distance is surpassed</li>"\
        "</ul></p>"
