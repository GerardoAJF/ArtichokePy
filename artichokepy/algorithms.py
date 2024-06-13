import abc
import typing as t
from artichokepy import Graph, Node
from artichokepy.graph import Relation

NodeSolutionType = t.Tuple[Node, t.List[Node]]

class Frontier(abc.ABC):
    def __init__(self) -> None:
        self.frontier = []

    def get_len(self) -> int:
        return len(self.frontier)

    @abc.abstractmethod
    def add_node(self, node: NodeSolutionType) -> None:
        pass

    @abc.abstractmethod
    def remove_node(self) -> NodeSolutionType:
        pass


class DFSFrontier(Frontier):
    def add_node(self, node: NodeSolutionType) -> None:
        self.frontier.append(node)

    def remove_node(self) -> NodeSolutionType:
        return self.frontier.pop()


class BFSFrontier(Frontier):
    def add_node(self, node: NodeSolutionType) -> None:
        self.frontier.append(node)

    def remove_node(self) -> NodeSolutionType:
        return self.frontier.pop(0)


class DijkstraFrontier(Frontier):
    pass

# * ===============================

class SearchAlgorithm:
    def __init__(self, frontier: Frontier) -> None:
        self.frontier = frontier
        self.exploration_set = set()

    def get_next_nodes(self, node: Node) -> set[Relation]:
        return set(node.relations)

    def search(self, graph: Graph, start: Node, end: Node) -> NodeSolutionType:
        self.frontier.add_node((start, []))
        self.exploration_set.add(start)

        while(self.frontier.get_len() != 0 and len(self.exploration_set) != len(graph.nodes)):

            actual_node = self.frontier.remove_node()
            self.exploration_set.add(actual_node[0])

            if actual_node[0] == end:
                return actual_node
                
            for relation in self.get_next_nodes(actual_node[0]):
                if relation.end not in self.exploration_set:
                    self.frontier.add_node((relation.end, [actual_node[0]] + actual_node[1]))
        
        return (Node(""), [])