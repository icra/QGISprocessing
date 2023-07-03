import networkx as nx

def extract_subgraph(nodes, arcs, node_id, node_1, node_2, edar_code, feedback):

    # 1. creem un graph amb la xarxa
    G = nx.DiGraph()
    G.add_nodes_from(
        [(feat[node_id], feat.__geo_interface__["properties"]) for feat in nodes.getFeatures() if feat['state'] != 0])
    G.add_edges_from(
        [(feat['node_1'], feat['node_2'], feat.__geo_interface__["properties"]) for feat in arcs.getFeatures() if
         feat['state'] != 0])

    # estem eliminant els obsolets escollint nomes els state=0 (OPERATIVO)

    feedback.setProgressText('The operational network contains: ')
    feedback.setProgressText(f"nodes =  {len(G.nodes)}")
    feedback.setProgressText(f"edges = {len(G.edges)}")

    #2 Extraiem la sub-xarxa connectada a la depuradora
    #2.1 Definim la depuradora
    # edar_code= 'PR0005300'
    # edar,data_edar=[(node,data) for node, data in G.nodes(data=True) if data['code'] == edar_code][0]
    # data_edar['epa_type']="OUTFALL"
    # data_edar['sys_type']="OUTFALL"
    # data_edar['node_type']="OUTFALL"

    #2.2 definim el subGraph associat:
    G_notDi = nx.Graph(G)
    connected_to_wwtp = nx.node_connected_component(G_notDi, edar_code)
    subGraph = G.subgraph(connected_to_wwtp)

    # Set outfall attributes to wwtp node
    new = 'OUTFALL'
    nx.set_node_attributes(subGraph, {edar_code: {'epa_type': new, 'sys_type': new, 'node_type': new}})

    feedback.setProgressText(f'The operational network connected to WWTP ({edar_code}) contains: ')
    feedback.setProgressText(f"nodes =  {len(subGraph.nodes)}")
    feedback.setProgressText(f"edges = {len(subGraph.edges)}")

    return subGraph
