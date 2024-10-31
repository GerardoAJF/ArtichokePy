import pytest
import sys

sys.path.append("../artichokepy")

from artichokepy.graph import *


# *==================NODES=====================


@pytest.fixture
def example_node():
    return Node(1, index=1)


@pytest.fixture
def example_nodes():
    a = Node(1, index=1)
    b = Node(2, index=2)

    return a, b


def test_node_getattr(example_node):
    assert example_node.value == 1
    assert example_node.index == 1


def test_node_comparison(example_nodes):
    example_nodes[0]._id = example_nodes[1]._id

    assert example_nodes[0] == example_nodes[1]


def test_node_hash(example_nodes):
    example_nodes[0]._id = example_nodes[1]._id

    assert example_nodes[0] in {example_nodes[1]}


def test_node_degree(example_nodes):
    example_nodes[0].add_relation((example_nodes[1], 10))
    example_nodes[1].add_relation((Node("C"), 10), (Node("D"), 20))

    assert example_nodes[1].input_degree == 1
    assert example_nodes[1].output_degree == 2


def test_node_add_relation(example_nodes):
    example_nodes[0].add_relation((example_nodes[1], 10), (Node(2), 2))

    relation = Relation(example_nodes[0], example_nodes[1], 10)

    assert relation in example_nodes[0].relations
    assert relation in example_nodes[1].parents


def test_node_remove_relation(example_nodes) -> None:
    example_nodes[0].add_relation((example_nodes[1], 10), (Node(2), 2))
    example_nodes[0].remove_relation(example_nodes[1])

    relation = Relation(example_nodes[0], example_nodes[1], 10)

    assert relation not in example_nodes[0].relations
    assert relation not in example_nodes[1].parents


def test_node_add_relation_bidirectional(example_nodes):
    example_nodes[0].add_relation(
        (example_nodes[1], 10), (Node(2), 2), bidirectional=True
    )

    relation = Relation(example_nodes[0], example_nodes[1], 10)
    reverse = Relation(example_nodes[1], example_nodes[0], 10)

    assert relation in example_nodes[0].relations
    assert relation in example_nodes[1].parents
    assert reverse in example_nodes[1].relations
    assert reverse in example_nodes[0].parents


def test_node_remove_relation_bidirectional(example_nodes):
    example_nodes[0].add_relation(
        (example_nodes[1], 10), (Node(3), 2), bidirectional=True
    )
    example_nodes[0].remove_relation(example_nodes[1], bidirectional=True)

    relation = Relation(example_nodes[0], example_nodes[1], 10)
    reverse = Relation(example_nodes[1], example_nodes[0], 10)

    assert relation not in example_nodes[0].relations
    assert relation not in example_nodes[1].parents
    assert reverse not in example_nodes[1].relations
    assert reverse not in example_nodes[0].parents


# *==================RELATIONS=====================


@pytest.fixture
def example_relation(example_nodes):
    return Relation(example_nodes[0], example_nodes[1], 100)


def test_relation_comparison(example_relation):
    assert example_relation == Relation(
        example_relation.init, example_relation.end, example_relation.weight
    )


def test_relation_reverse(example_relation):
    assert example_relation.reverse() == Relation(
        example_relation.end, example_relation.init, example_relation.weight
    )


# *==================GRAPHS=====================


def test_graph_eulerian_path():
    graph = Graph()

    a, b, c = graph.add_node("A", "B", "C")

    a.add_relation((b, 0), bidirectional=True)
    b.add_relation((c, 0), bidirectional=True)

    assert graph.eulerian_path() == True


def test_graph_eulerian_cycle():
    graph = Graph()

    a, b, c = graph.add_node("A", "B", "C")

    a.add_relation((b, 0))
    b.add_relation((c, 0))
    c.add_relation((a, 0))

    assert graph.eulerian_path() == True


def test_graph_no_eulerian():
    graph = Graph()

    a, b, c, d = graph.add_node("A", "B", "C", "D")

    a.add_relation((b, 0), (c, 0), (d, 0))
    b.add_relation((a, 0), (d, 0))
    c.add_relation((a, 0))
    c.add_relation((c, 0))

    assert graph.eulerian_path() == False


def test_graph_hamiltonian():
    graph = Graph()

    a, b, c = graph.add_node("A", "B", "C")

    a.add_relation((b, 0))
    b.add_relation((c, 0))
    c.add_relation((a, 0))

    assert graph.hamiltonian_cycle() == True


def test_graph_no_hamiltonian():
    graph = Graph()

    a, b, c, d = graph.add_node("A", "B", "C", "D")

    a.add_relation((b, 0), bidirectional=True)
    b.add_relation((c, 0), (d, 0), bidirectional=True)

    assert graph.hamiltonian_cycle() == False


def test_graph_density():
    graph = Graph()

    a, b, c, d = graph.add_node("A", "B", "C", "D")

    a.add_relation((b, 0), (c, 0), (d, 0))
    b.add_relation((a, 0), (c, 0), (d, 0))
    c.add_relation((a, 0), (b, 0), (d, 0))
    d.add_relation((a, 0), (b, 0), (c, 0))

    assert graph.density == 1


def test_graph_weighted_density():
    graph = Graph()

    a, b, c, d = graph.add_node("A", "B", "C", "D")

    a.add_relation((b, 10), (c, 0), (d, 10))
    b.add_relation((a, 10), (c, 0), (d, 10))
    c.add_relation((a, 10), (b, 0), (d, 0))
    d.add_relation((a, 10), (b, 0), (c, 0))

    assert graph.density == 5


def test_graph_add_node_value():
    graph = Graph()
    a = graph.add_node("A")[0]

    assert a in graph.nodes


def test_graph_add_node_copy():
    graph = Graph()
    a = graph.add_node("A")[0]

    graph2 = Graph()
    graph2.add_node(a)[0]

    assert a in graph2.nodes


def test_graph_add_node_mix():
    graph = Graph()
    a = graph.add_node("A")[0]

    graph2 = Graph()
    _, b = graph2.add_node(a, "B")

    assert a in graph2.nodes
    assert b in graph2.nodes


def test_graph_remove_node():
    graph = Graph()

    a, b = graph.add_node("A", "B")
    a.add_relation((b, 0))

    graph.remove_node(b)

    assert b not in graph.nodes
    assert Relation(a, b, 0) not in a.relations


def test_graph_get_centrality_nodes_central():
    graph = Graph()

    a, b, c, d = graph.add_node("A", "B", "C", "D")

    a.add_relation((b, 0), bidirectional=True)
    b.add_relation((c, 0), (d, 0), bidirectional=True)

    assert graph.get_centrality_nodes("central") == {b}


def test_graph_get_centrality_nodes_border():
    graph = Graph()

    a, b, c, d = graph.add_node("A", "B", "C", "D")

    a.add_relation((b, 0), bidirectional=True)
    b.add_relation((c, 0), (d, 0), bidirectional=True)

    assert graph.get_centrality_nodes("border") == {a, c, d}


def test_graph_get_relations():
    graph = Graph()

    a, b, c = graph.add_node("A", "B", "C")

    a.add_relation((b, 0))
    b.add_relation((c, 5))
    c.add_relation((a, 2))

    assert Relation(a, b, 0) in graph.relations
    assert Relation(b, c, 5) in graph.relations
    assert Relation(c, a, 2) in graph.relations


def test_graph_set_relations():
    a, b, c = Node("A"), Node("B"), Node("C")

    graph = Graph()
    graph.relations = {Relation(a, b, 0), Relation(a, c, 0)}

    assert graph.nodes == {a, b, c}

    assert graph.adjacency_matrix[a][b] == 1
    assert graph.adjacency_matrix[a][c] == 1


def test_graph_adjacency_matrix():
    graph = Graph()

    a, b, c = graph.add_node("A", "B", "C")

    a.add_relation((b, 0))
    b.add_relation((c, 5))
    c.add_relation((a, 2))

    assert graph.adjacency_matrix[a][b] == 1
    assert graph.adjacency_matrix[b][c] == 1
    assert graph.adjacency_matrix[c][a] == 1


def test_graph_adjacency_list():
    graph = Graph()

    a, b, c = graph.add_node("A", "B", "C")

    a.add_relation((b, 0))
    b.add_relation((c, 5), (a, 2))

    assert b in graph.adjacency_list[a]

    assert c in graph.adjacency_list[b]
    assert a in graph.adjacency_list[b]


def test_graph_comparison():
    graph1 = Graph()
    a, b, c = graph1.add_node("A", "B", "C")

    a.add_relation((b, 0), (c, 0))

    graph2 = Graph()
    one, two, three = graph2.add_node(1, 2, 3)

    one.add_relation((two, 0), (three, 0))

    assert graph1 == graph2


def test_graph_hash():
    graph1 = Graph()
    a, b, c = graph1.add_node("A", "B", "C")

    a.add_relation((b, 0), (c, 0))

    graph2 = Graph()
    graph2._id = graph1._id
    one, two, three = graph2.add_node(1, 2, 3)

    one.add_relation((two, 0), (three, 0))

    assert hash(graph1) == hash(graph2)


def test_graph_sum():
    graph1 = Graph()
    a, b, c = graph1.add_node("A", "B", "C")
    a.add_relation((b, 0), (c, 0))

    graph2 = Graph()
    one, two = graph2.add_node(1, 2)
    one.add_relation((two, 0))

    graph3 = graph1 + graph2

    assert graph1.nodes.issubset(graph3.nodes)
    assert graph2.nodes.issubset(graph3.nodes)

    assert graph1.relations.issubset(graph3.relations)
    assert graph2.relations.issubset(graph3.relations)


def test_graph_subtract():
    graph1 = Graph()
    a, b, c = graph1.add_node("A", "B", "C")
    a.add_relation((b, 0), (c, 0))

    graph2 = Graph()
    one, two = graph2.add_node(a, c)
    one.add_relation((two, 0))

    graph3 = graph1 - graph2

    assert graph3.nodes == graph1.nodes.difference({two})
    assert graph3.relations == graph1.relations.difference({Relation(one, two, 0)})


def test_print_adjacent_matrix(capsys):

    graph1 = Graph()
    cero, one = graph1.add_node("0", "1")
    cero.add_relation((one, 0), bidirectional=True)

    print_adjacent_matrix(graph1)
    captured = capsys.readouterr().out

    expected_output1 = (
        "@ 0 1\n"
        "0 0 1 \n"  
        "1 1 0 \n"
        "-----\n"
    )

    expected_output2 = (
        "@ 1 0\n"
        "1 0 1 \n"  
        "0 1 0 \n"
        "-----\n"
    )

    assert (captured == expected_output1) or (captured == expected_output2)
