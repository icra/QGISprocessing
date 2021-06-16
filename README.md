# buildings2sewer

## 'buildings2sewer' is a QGIS processing plugin that connects the buildings of a city to the manholes of the sewer system. It connects each building (using the centroid as a departure point) to the closest manhole that is in the same or in a lower altitude.

It returns the centroids of the buildings with the following fields:

  - Id of the manhole which the building is connected
  - Altitude of the building's centroid
  - Distance between the building's centroid and the connected manhole
  - Altitude difference between the building's centroid and the connected manhole

If "Create connection lines is checked", it also returns a layer with the lines showing each connection.

Two parameters can be adjusted:

  - Maximum distance: If a connection is larger than the maximum distance, the algorithm searches manholes 1 meter above. This iteration is repeated until the connection is shorter than the maximum distance or until the altitude tolerance is reached
  - Altitude tolerance: It determines how many meters upper a manhole can be regarding the building to connect. The altitude tolerance is only used when the maximum distance is surpassed
