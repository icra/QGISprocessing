import networkx as nx
from .update_changed_field import update_changed_field
def correct_directions(subGraph, edar_code, node_id, node_1, node_2, feedback):
    # nodes marcats com OUTFALL
    outfalls = [node for node, data in subGraph.nodes(data=True) if data['epa_type'] == 'OUTFALL']
    # nodes marcats com CHAMBERS i son inici de xarxa
    # TODO: Això ha de ser definit per l'usuari, com fer-ho?
        # Podem utilitzar el sys_type? Potser és més stàndard?
    chambers_netinit = [node for node, data in subGraph.nodes(data=True) if data['nodecat_id'] == 'CEC' and subGraph.degree(node) == 1]

    # S'intercanvien els valors del node 1 i node 2 de l'aresta
    # TODO: Podem girar només node_1 i node_2, que son els camps que demanem a l'usuari? Els altres s'utilitzen? O es poden calcular un cop invertida la direcció?
    # attributes = ['node_', 'y', 'custom_y', 'elev', 'custom_elev', 'sys_elev', 'nodetype_', 'sys_y', 'r', 'z']
    attributes = [node_1, node_2]

    # Per direccionar els arcs del subGraph que no arriben a la depuradora o als nodes de sobreiximent
    # 1. Trobem tots els nodes que no arriben a la depuradora
    # 2. Trobem els nodes del punt 1 que no arriben a cap outfall/chamberNETINIT
    no_llegan_depuradora = [node for node in subGraph.nodes if not nx.has_path(subGraph, node, edar_code)]

    no_llegan_outfall = []
    for node in no_llegan_depuradora:
        outfalls_i_chambers = outfalls + chambers_netinit
        if node not in outfalls_i_chambers:
            llega = False
            i = 0
            while not llega and len(outfalls_i_chambers) > i:
                llega = nx.has_path(subGraph, node, outfalls_i_chambers[i])
                i += 1
            if not llega:
                no_llegan_outfall.append(node)

    feedback.setProgressText(f"Nodes not connected to WWTP = {len(no_llegan_depuradora)}")
    feedback.setProgressText(f"Nodes not connected to WWTP or outfall or chamberNETINIT = {len(no_llegan_outfall)}")

    # malament = no_llegan_outfall.copy()

    # 3. Mentre hi hagi nodes que no arribin a la depuradora ni a un outfall
    # 3.1 Per tots aquests nodes
    # 3.1.1 Mirem si els seus veins arriben a la depuradora
    # 3.1.2 Si algun vei arriba a la depuradora, afegim un nou arc que va del node al vei i eliminem l'antic
    # 3.2 Si cap dels seus veins arriba a la depuradora, s'afegeix de nou a la llista  de nodes a revisar
    arcs_girats = []
    while len(no_llegan_outfall) > 0:
        no = []
        for node in no_llegan_outfall:
            teCami = nx.has_path(subGraph, node, edar_code)
            if not teCami:
                veins = list(nx.all_neighbors(subGraph, node))
            while not teCami and len(veins) > 0:
                v = veins.pop()
                teCami = nx.has_path(subGraph, v, edar_code)
                if teCami and subGraph.has_edge(v, node):
                    data = reverse_nodes(subGraph.get_edge_data(v, node), node_1, node_2)
                    data['reversed'] = True
                    feedback.setProgressText(f"Edge reversed: {v} - {node}")
                    changed = update_changed_field(subGraph, (v, node), 'edge', ['reversed', node_1, node_2])
                    data['changed'] = changed
                    subGraph.add_edge(node, v, **data)
                    subGraph.remove_edge(v, node)
                    # arcs_girats.append(data[(v[node_id], node[node_id])])
            if not teCami:
                no.append(node)
        no_llegan_outfall = no

    # Si tornem a veure els nodes que no arriben a la depuradora, haurien de quedar 1 (la depuradora)

    no_llegan_depuradora_arreglat = [node for node in subGraph.nodes if not nx.has_path(subGraph, node, edar_code)]

    no_llegan_outfall_arreglat = []
    for node in no_llegan_depuradora_arreglat:
        if node not in outfalls:
            llega = False
            i = 0
            while not llega and len(outfalls) > i:
                llega = nx.has_path(subGraph, node, outfalls[i])
                i += 1
            if not llega:
                no_llegan_outfall_arreglat.append(node)

    feedback.setProgressText(f"Nodes not connected to WWTP after rerouting = {len(no_llegan_depuradora_arreglat)}")
    feedback.setProgressText(f"Nodes not connected to WWTP or outfall after rerouting = {len(no_llegan_outfall_arreglat)}")

    return subGraph

def reverse_nodes(data, node_1, node_2):
    node_1_old = data[node_2]
    node_2_old = data[node_1]
    data[node_1] = node_2_old
    data[node_2] = node_1_old

    # for attribute in attributes:
    #     if attribute + '1' in data:
    #         aux = data[attribute + '1']
    #         data[attribute + '1'] = data[attribute + '2']
    #         data[attribute + '2'] = aux
    # if 'geometry' in data:
    #     data['geometry'] = reverse(data['geometry'])
    return data