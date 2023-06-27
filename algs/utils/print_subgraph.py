from shapely import LineString
from pyproj import CRS, Transformer
import networkx as nx
import momepy as mm
import geopandas as gpd


def print_subgraph(subGraph):
    subGraph_copy = subGraph.copy()

    # Transform coordinates
    transformer = Transformer.from_crs("EPSG:25831", "WGS84")
    for index, row in subGraph_copy.nodes(data=True):
        if row['state'] != 0:
            x = row['geometry'].x
            y = row['geometry'].y
            long, lat = transformer.transform(x, y)
            row['longitude'] = long
            row['latitude'] = lat
            row['x'] = x
            row['y'] = y
            row['geometry'] = (lat, long)

    geometry_nodes = {node: data['geometry'] for node, data in subGraph_copy.nodes(data=True)}
    subGraph_copy = nx.relabel_nodes(subGraph_copy, geometry_nodes)
    points, lines = mm.nx_to_gdf(subGraph_copy)

    points.set_geometry("geometry")

    lines.set_geometry("geometry")
    lines.crs = CRS.from_epsg(25831)  # Set the CRS information for the lines layer

    return points, lines

