import pytest
import sys

sys.path.append("../artichokepy")

from artichokepy.search import *
from artichokepy.graph import *


# *==================NODE SOLUTION=====================


@pytest.fixture
def nodes():
    graph = Graph()

    a, b, c = graph.add_node("A", "B", "C")

    a.add_relation((b, 5), (c, 10))
    return a, b, c


def test_node_solution_add_steps(nodes):
    a, b, c = nodes

    node_solution = NodePath(a)

    node_solution.add_steps(Relation(a, b, 0), Relation(b, c, 0))

    assert node_solution.path == [
        Relation(a, b, 0),
        Relation(b, c, 0),
    ]
    assert node_solution.nodes == {a, b, c}


def test_node_solution_get_previous_node(nodes):
    a, b, c = nodes

    node_solution = NodePath(a)

    node_solution.add_steps(Relation(c, b, 0), Relation(b, a, 0))

    assert node_solution.get_previous_node(1) == b
    assert node_solution.get_previous_node(2) == c


def test_node_solution_comparison(nodes):
    a, b, _ = nodes

    node_solution = NodePath(a)
    assert node_solution == NodePath(a)

    node_solution.add_steps(Relation(b, a, 5))
    assert node_solution != NodePath(a)
    assert node_solution == NodePath(a).add_steps(Relation(b, a, 5))


def test_node_solution_hash(nodes):
    a, b, _ = nodes

    node_solution = NodePath(a)
    assert hash(node_solution) == hash(NodePath(a))

    node_solution.add_steps(Relation(b, a, 5))
    assert hash(node_solution) != hash(NodePath(a))
    assert hash(node_solution) == hash(NodePath(a).add_steps(Relation(b, a, 5)))


# *==================FRONTIERS=====================


@pytest.fixture
def node_solutions():
    a = Node("A", color=2)
    b = Node("B", color=3)
    c = Node("C", color=1)

    return (
        NodePath(a),
        NodePath(b).add_steps(Relation(a, b, 3)),
        NodePath(c).add_steps(Relation(b, c, 6)),
    )


def test_dfs_frontier(node_solutions):
    a, b, c = node_solutions

    frontier = DFSFrontier()

    frontier.add_node(a)
    frontier.add_node(b)
    frontier.add_node(c)

    assert frontier.frontier == [a, b, c]
    assert frontier.get_len() == 3

    frontier.remove_node()

    assert frontier.frontier == [a, b]

    frontier.clear()

    assert frontier.frontier == []


def test_bfs_frontier(node_solutions):
    a, b, c = node_solutions

    frontier = BFSFrontier()

    frontier.add_node(a)
    frontier.add_node(b)
    frontier.add_node(c)

    assert frontier.frontier == [a, b, c]
    assert frontier.get_len() == 3

    frontier.remove_node()

    assert frontier.frontier == [b, c]

    frontier.clear()

    assert frontier.frontier == []


def test_auto_sort_frontier(node_solutions):
    a, b, c = node_solutions

    frontier = AutoSortFrontier(lambda x: x.node.color)

    frontier.add_node(b)
    frontier.add_node(c)
    frontier.add_node(a)
    assert frontier.frontier == [c, a, b]

    frontier.remove_node()
    assert frontier.frontier == [a, b]

    frontier.add_node(c)
    assert frontier.frontier == [c, a, b]


def test_dijkstra_frontier(node_solutions):
    a, b, c = node_solutions

    frontier = DijkstraFrontier()

    frontier.add_node(b)
    frontier.add_node(c)
    frontier.add_node(a)
    assert frontier.frontier == [a, b, c]

    frontier.remove_node()
    assert frontier.frontier == [b, c]

    frontier.add_node(a)
    assert frontier.frontier == [a, b, c]


def test_greedy_frontier(node_solutions):
    a, b, c = node_solutions

    heuristic = HeuristicFunction()
    heuristic.set_function(lambda x: x.node.color)

    frontier = GreedyFrontier(heuristic)

    frontier.add_node(b)
    frontier.add_node(c)
    frontier.add_node(a)
    assert frontier.frontier == [c, a, b]

    frontier.remove_node()
    assert frontier.frontier == [a, b]

    frontier.add_node(c)
    assert frontier.frontier == [c, a, b]


def test_a_star_frontier(node_solutions):
    a, b, c = node_solutions

    heuristic = HeuristicFunction()
    heuristic.set_function(lambda x: x.node.color)

    frontier = AStarFrontier(PathCost(), heuristic)

    frontier.add_node(b)
    frontier.add_node(c)
    frontier.add_node(a)
    assert frontier.frontier == [a, b, c]

    frontier.remove_node()
    assert frontier.frontier == [b, c]

    frontier.add_node(a)
    assert frontier.frontier == [a, b, c]


# *==================FUNCTIONS=====================


@pytest.fixture
def graph():
    graph = Graph()

    a, b, c, d, e = graph.add_node("A", "B", "C", "D", "E")

    a.add_relation((b, 5), (c, 10))
    b.add_relation((d, 6))
    c.add_relation((e, 15))
    d.add_relation((e, 4))

    return graph


def test_cost_function():

    def cost_function(node: NodePath):
        return node.node.color

    cost = CostFunction()
    cost.set_function(cost_function)

    assert cost(NodePath(Node("A", color=12))) == 12


def test_path_cost():
    a, b, c = Node("A"), Node("B"), Node("C")
    solution = NodePath(c).add_steps(Relation(a, b, 10), Relation(b, c, 5))

    assert PathCost()(solution) == 15


def test_heuristic_function_check_scale(graph):
    heuristic = HeuristicFunction()

    heuristic.set_function(lambda x: 10)
    assert heuristic.check_scale(graph) < 0.6
    assert heuristic.check_scale(graph) > 0.4

    heuristic.set_function(lambda x: 1000)
    assert heuristic.check_scale(graph) > 0.9


def test_heuristic_function_is_admissible(graph):
    heuristic = HeuristicFunction()

    def heuristic_function(node: NodePath):
        return PathCost()(node) + 1

    heuristic.set_function(heuristic_function)
    assert not heuristic.is_admissible(graph)

    heuristic.set_function(lambda x: 0)
    assert heuristic.is_admissible(graph)


def test_heuristic_function_is_consistent(graph):
    heuristic = HeuristicFunction()
    cost = CostFunction()
    cost.set_function(lambda x: 0)

    heuristic.set_function(PathCost())
    assert not heuristic.is_consistent(graph, cost)

    heuristic.set_function(lambda x: 0)
    assert heuristic.is_consistent(graph)


# *==================STATE=====================


def test_heuristic_function_add_state():
    heuristic = HeuristicFunction()
    e, o = heuristic.add_state(("even", 0), ("odd", 1))

    assert "even" in heuristic.states.keys()
    assert "odd" in heuristic.states.keys()

    assert e in heuristic.states.values()
    assert o in heuristic.states.values()


def test_heuristic_function_subscribe_state():
    heuristic = HeuristicFunction()
    e, o = heuristic.add_state(("even", 0), ("odd", 1))

    def update_value(state: State, step=2):
        return state.value + step

    e.add_update_func(update_value)
    o.add_update_func(update_value, step=4)

    @heuristic.subscribe_state(e, "odd")
    def manual_activation():
        print("update states")

    manual_activation()
    assert e.value == 2 and o.value == 5

    manual_activation()
    assert e.value == 4 and o.value == 9


# *==================SEARCH ALGORITHM=====================


@pytest.fixture
def graph_nodes():
    graph = Graph()

    a, b, c, d, e = graph.add_node("A", "B", "C", "D", "E")

    a.add_relation((b, 5), (c, 10))
    b.add_relation((d, 6))
    c.add_relation((e, 15))
    d.add_relation((e, 4))

    return graph, a, b, c, d, e


def test_search_algorithm_get_next_nodes(nodes):
    a, b, c = nodes
    search = SearchAlgorithm(DijkstraFrontier())
    assert search.get_next_nodes(a) == {Relation(a, b, 5), Relation(a, c, 10)}


def test_search_algorithm_search(graph_nodes):
    graph, a, b, _, d, _ = graph_nodes

    search = SearchAlgorithm(BFSFrontier())

    assert search.search(graph, a, d) == NodePath(d).add_steps(
        Relation(a, b, 5), Relation(b, d, 6)
    )


def test_search_algorithm_search_all(graph_nodes):
    _, a, b, c, d, e = graph_nodes

    d.add_relation((b, 2))
    search = SearchAlgorithm(BFSFrontier())

    assert search.search_all(a, e) == {
        NodePath(e).add_steps(Relation(a, b, 5), Relation(b, d, 6), Relation(d, e, 4)),
        NodePath(e).add_steps(Relation(a, c, 10), Relation(c, e, 15)),
    }


def test_search_reset(graph_nodes):
    graph, a, b, c, d, _ = graph_nodes

    search = SearchAlgorithm(BFSFrontier())

    search.search(graph, a, d)
    assert search.exploration_set.issuperset({a, b, c, d})

    search.reset()
    assert search.exploration_set == set()
