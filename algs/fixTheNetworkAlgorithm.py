# -*- coding: utf-8 -*-

"""
/***************************************************************************
 fixTheNetwork
                                 A QGIS plugin
 Reconcile and fix a sewer network to ensure the water flow from all nodes to
 wastewater treatment plan
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-06-15
        copyright            : (C) 2021 by Ruben Oncala, ICRA
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

__author__ = 'Ruben Oncala (ICRA), Sergi Bergillos (UdG) & Josep Pueyo-Ros (ICRA)'
__date__ = '2023-06-23'
__copyright__ = '(C) 2023 by Ruben Oncala, ICRA'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import *
from PyQt5.QtGui import QIcon
from qgis.core import *
import qgis.utils
import processing
import os
from .utils.check_extent import check_extent
from .utils.z_sampling import z_sampling
from .utils.extract_subgraph import extract_subgraph  
from .utils.print_subgraph import print_subgrap        

pluginPath = os.path.dirname(__file__)

class fixTheNetworkAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'
    NODES = 'NODES'
    ARCS = 'ARCS'
    FIXED_NODES = 'FIXED_NODES'
    FIXED_ARCS = 'FIXED_ARCS'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        # Add layer of nodes
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.NODES,
                self.tr('Manholes (network nodes)'),
                [QgsProcessing.TypeVectorPoint]
            )
        )

        # Add layer of arcs
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.ARCS,
                self.tr('Segments (network arcs'),
                [QgsProcessing.TypeVectorLine]
            )
        )

        # Define field of node_id
        self.addParameter(
            QgsProcessingParameterField(
                'node_id',
                self.tr('Field with manholes id'),
                parentLayerParameterName=self.NODES,
                allowMultiple=False
            )
        )

        # Define from field in arcs
        self.addParameter(
            QgsProcessingParameterField(
                'from',
                self.tr('FROM field in segments'),
                parentLayerParameterName=self.ARCS,
                allowMultiple=False
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                'to',
                self.tr('TO field in segments'),
                parentLayerParameterName=self.ARCS,
                allowMultiple=False
            )
        )

        self.addParameter(
            QgsProcessingParameterRasterLayer(
                'DEM',
                self.tr('Elevations raster')
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.FIXED_NODES,
                self.tr('Fixed nodes'),
                type = QgsProcessing.TypeVectorPoint
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.FIXED_ARCS,
                self.tr('Fixed arcs'),
                type = QgsProcessing.TypeVectorLine
            )
        )

    # modifico nomes aquesta funcio
    def processAlgorithm(self, parameters, context, feedback):
        """
        1. read the network data and extract the subgraph connected to EDAR:
           - disconnected pluvial network, orphan nodos or inoperative segments are excluded
        2. print the subgraph
        """
        feedback.setProgressText("Processing...")

        # Load layers
        nodes = self.parameterAsVectorLayer(parameters, self.NODES, context)
        arcs = self.parameterAsVectorLayer(parameters, self.ARCS, context)
        mde = self.parameterAsRasterLayer(parameters, 'DEM', context)

        # Extract the subgraph
        subGraph = extract_subgraph(node=nodes, arc=arcs, edar_code='PR0005300')
        # TODO: edar_code hauria de ser un string que l'usurai defineix en el plugin, deixem el nostre per defecte 

        # imprimim el subgraph
        subgraph_points, subgraph_lines = print_subgraph(subGraph)

        # Create FIXED_NODES sink
        (sink_fixed_nodes, sink_fixed_nodes_id) = self.parameterAsSink(parameters, self.FIXED_NODES,
                context, subgraph_points.fields(), subgraph_points.wkbType(), subgraph_points.sourceCrs())

        # Create FIXED_ARCS sink
        (sink_fixed_arcs, sink_fixed_arcs_id) = self.parameterAsSink(parameters, self.FIXED_ARCS,
                context, subgraph_lines.fields(), subgraph_lines.wkbType(), subgraph_lines.sourceCrs())

        # Write the fixed nodes and arcs to the sinks
        sink_fixed_nodes.addFeatures(subgraph_points.getFeatures())
        sink_fixed_arcs.addFeatures(subgraph_lines.getFeatures())

        return {self.FIXED_ARCS: sink_fixed_arcs_id, self.FIXED_NODES: sink_fixed_nodes_id}

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'fixTheNetwork'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def icon(self):
        return QIcon(os.path.join(pluginPath, '..', 'icons', 'fixthenetwork.png'))

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return fixTheNetworkAlgorithm()

    # TODO: Change help (html format)
    def shortHelpString(self):
        return "<p>General description</p>"\
        "<p>Description of the layers it returns</p>"\
        "<p>Description of input parameters using <ul></p>"
