import pytest
import sys

sys.path.append("../artichokepy")

from artichokepy.algorithms import *
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
    
    node_solution = NodeSolution(a)

    node_solution.add_steps(
        Relation(c, b, 0), Relation(b, a, 0)
    )

    assert node_solution.path == [
        Relation(c, b, 0),
        Relation(b, a, 0),
    ]


def test_node_solution_get_previous_node(nodes):
    a, b, c = nodes

    node_solution = NodeSolution(a)

    node_solution.add_steps(
        Relation(c, b, 0), Relation(b, a, 0)
    )

    assert node_solution.get_previous_node(1) == b
    assert node_solution.get_previous_node(2) == c


def test_node_solution_comparison(nodes):
    a, b, _ = nodes
    
    node_solution = NodeSolution(a)
    assert node_solution == NodeSolution(a)
    
    node_solution.add_steps(Relation(b, a, 5))
    assert node_solution != NodeSolution(a)
    assert node_solution == NodeSolution(a).add_steps(Relation(b, a, 5))
    
    
def test_node_solution_hash(nodes):
    a, b, _ = nodes
    
    node_solution = NodeSolution(a)
    assert hash(node_solution) == hash(NodeSolution(a))
    
    node_solution.add_steps(Relation(b, a, 5))
    assert hash(node_solution) != hash(NodeSolution(a))
    assert hash(node_solution) == hash(NodeSolution(a).add_steps(Relation(b, a, 5)))


# *==================FRONTIERS=====================


@pytest.fixture
def node_solutions():
    a = Node("A", color=2)
    b = Node("B", color=3)
    c = Node("C", color=1)

    return (
        NodeSolution(a),
        NodeSolution(b).add_steps(Relation(a, b, 3)),
        NodeSolution(c).add_steps(Relation(b, c, 6)),
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

    def cost_function(node: NodeSolution):
        return node.node.color

    cost = CostFunction()
    cost.set_function(cost_function)

    assert cost(NodeSolution(Node("A", color=12))) == 12


def test_path_cost():
    a, b, c = Node("A"), Node("B"), Node("C")
    solution = NodeSolution(c).add_steps(Relation(a, b, 10), Relation(b, c, 5))

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

    def heuristic_function(node: NodeSolution):
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
    assert search.get_next_nodes(a) == {
        Relation(a, b, 5), 
        Relation(a, c, 10)}
    
    
def test_search_algorithm_search(graph_nodes):
    graph, a, b, _, d, _ = graph_nodes
    
    search = SearchAlgorithm(BFSFrontier())
    
    assert search.search(graph, a, d) == NodeSolution(d).add_steps(Relation(a, b, 5), Relation(b, d, 6))


def test_search_reset(graph_nodes):
    graph, a, b, c, d, _ = graph_nodes
    
    search = SearchAlgorithm(BFSFrontier())
    
    search.search(graph, a, d)
    assert search.exploration_set.issuperset({a, b, c, d})
    
    search.reset()
    assert search.exploration_set == set()