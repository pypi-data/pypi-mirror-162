import networkx as nx

from orkg import ORKG
from orkg.graph.base import ORKGEdge, ORKGNode


def subgraph(client: ORKG, thing_id: str) -> nx.DiGraph:
    """
    Obtains a networkx directed graph representation of any ORKG component given by its thing_id.
    E.g. of ORKG components: Paper, Contribution, Comparison, Template

    It starts from the thing_id resource and recursively traverses the graph until all literals
    or an already visited node has been found.

    :param client: orkg.ORKG client used to connect with ORKG backend.
    :param thing_id: Any subject, object, predicate ID in the ORKG.
    """
    response = client.statements.bundle(thing_id)

    if not response.succeeded:
        raise ValueError('Something went wrong while connecting to ORKG backend with host {}'.format(client.host))

    root_id = response.content['root']
    statements = response.content['statements']
    root_node = _create_root_node(root_id, statements)

    try:
        return _construct_subgraph(nx.DiGraph(), root_node, statements)
    except RecursionError:
        raise ValueError('The given resource is too deep, try to iteratively get its subgraphs. '
                         'This can e.g. happen when you are trying to fetch a subgraph of an ORKG List '
                         'containing a large number of ORKG Papers.')


def _create_root_node(root_id: str, statements: list) -> ORKGNode:
    """
    Creates an ORKGNode from the subject of the first statement with subject_id == root_id.

    :param root_id: ID of the root node.
    :param statements: List of all statements describing the subgraph.
    """
    for statement in statements:
        if statement['subject']['id'] == root_id:
            return _create_node_from_thing(statement['subject'])

    raise ValueError('Nothing found for the provided ID: {}'.format(root_id))


def _construct_subgraph(subgraph: nx.DiGraph, root_node: ORKGNode, statements: list) -> nx.DiGraph:
    """
    Recursively constructs a subgraph starting from the root_node and traversing to the target nodes found in
    the statements.

    :param subgraph: Initial networkx.DiGraph to extend with nodes and edges.
    :param root_node: Node to start with.
    :param statements: List of all statements describing the subgraph.
    """
    connecting_statements = [s for s in statements if s['subject']['id'] == root_node.id]

    for statement in connecting_statements:
        target_node = _create_node_from_thing(statement['object'])
        predicate = _create_edge_from_thing(statement['predicate'])

        subgraph.add_edge(root_node, target_node, predicate=predicate)
        _construct_subgraph(subgraph, target_node, statements)

    return subgraph


def _create_node_from_thing(thing: dict) -> ORKGNode:
    return ORKGNode(
        id=thing['id'],
        label=thing['label'],
        class_=thing['_class'],
        classes=thing.get('classes', []),
        description=thing.get('description', ''),
        datatype=thing.get('datatype', '')
    )


def _create_edge_from_thing(thing: dict) -> ORKGEdge:
    return ORKGEdge(
        id=thing['id'],
        label=thing['label'],
        class_=thing['_class'],
    )
