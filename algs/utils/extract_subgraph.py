import networkx as nx

def extract_subgraph(node,arc,edar_code='PR0005300'):

    # 1. creem un graph amb la xarxa
    G = nx.DiGraph()
    G.add_nodes_from([(row['node_id'], row) for index, row in node.iterrows() if row['state']!=0])
    G.add_edges_from([(row['node_1'], row['node_2'], row) for index, row in arc.iterrows() if row['state']!=0])
    # estem eliminant els obsolets escollint nomes els state=0 (OPERATIVO)

    print('La xarxa OPERATIVA completa conte: ')
    print(f"nodes =  {len(G.nodes)}")
    print(f"arcs = {len(G.edges)}")

    #2 Extraiem la sub-xarxa connectada a la depuradora
    #2.1 Definim la depuradora
    edar_code= 'PR0005300'
    edar,data_edar=[(node,data) for node, data in G.nodes(data=True) if data['code'] == edar_code][0]
    data_edar['epa_type']="OUTFALL"
    data_edar['sys_type']="OUTFALL"
    data_edar['node_type']="OUTFALL"

    #2.2 definim el subGraph associat:
    G_notDi = nx.Graph(G)
    subGraph = nx.DiGraph(nx.subgraph(G,nx.node_connected_component(G_notDi, edar)))

    print(f'La xarxa OPERATIVA connectada a la depuradora ({edar_code}) conte: ')
    print(f"nodes =  {len(subGraph.nodes)}")
    print(f"arcs = {len(subGraph.edges)}")

    return subGraph
