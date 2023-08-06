import networkx as nx

from typing import Tuple

from orkg import ORKG


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
    subgraph, root_node = _create_root_node(nx.DiGraph(), root_id, statements)

    try:
        return _construct_subgraph(subgraph, root_node, statements)
    except RecursionError:
        raise ValueError('The given resource is too deep, try to iteratively get its subgraphs. '
                         'This can e.g. happen when you are trying to fetch a subgraph of an ORKG List '
                         'containing a large number of ORKG Papers.')


def _create_root_node(subgraph: nx.DiGraph, root_id: str, statements: list) -> Tuple[nx.DiGraph, str]:
    """
    Creates a node from the subject of the first statement with subject_id == root_id.

    :param root_id: ID of the root node.
    :param statements: List of all statements describing the subgraph.
    """
    for statement in statements:
        if statement['subject']['id'] == root_id:
            return subgraph, _create_node_from_thing(subgraph, statement['subject'])

    raise ValueError('Nothing found for the provided ID: {}'.format(root_id))


def _construct_subgraph(subgraph: nx.DiGraph, root_node: str, statements: list) -> nx.DiGraph:
    """
    Recursively constructs a subgraph starting from the root_node and traversing to the target nodes found in
    the statements.

    :param subgraph: Initial networkx.DiGraph to extend with nodes and edges.
    :param root_node: Node to start with.
    :param statements: List of all statements describing the subgraph.
    """
    connecting_statements = [s for s in statements if s['subject']['id'] == root_node]

    for statement in connecting_statements:
        target_node = _create_node_from_thing(subgraph, statement['object'])
        _create_edge(subgraph, root_node, target_node, statement['predicate'])
        _construct_subgraph(subgraph, target_node, statements)

    return subgraph


def _create_node_from_thing(subgraph: nx.DiGraph, thing: dict) -> str:
    subgraph.add_node(
        node_for_adding=thing['id'],
        id=thing['id'],
        label=thing['label'],
        class_=thing['_class'],
        classes=thing.get('classes', []),
        description=thing.get('description', ''),
        datatype=thing.get('datatype', '')
    )
    return thing['id']


def _create_edge(subgraph: nx.DiGraph, root_node: str, target_node: str, predicate) -> None:
    subgraph.add_edge(
        root_node,
        target_node,
        id=predicate['id'],
        label=predicate['label'],
        class_=predicate['_class'],
    )
