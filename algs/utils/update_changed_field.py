import networkx as nx

def update_changed_field(graph, id, element, list):
    '''
    id must be the id of the node or edge
    element must be one of 'node' or 'edge'
    list is the list of fields that have been updated

    Returns a list that must be used to update the field 'changed' in the node or edge updated
    '''

    if element == 'node':
        changed = nx.get_node_attributes(graph, 'changed')
    elif element == 'edge':
        changed = nx.get_edge_attributes(graph, 'changed')
    else:
        raise Exception('element must be node or edge')

    if changed.get(id) is None:
        return list
    else:
        return changed[id] + list