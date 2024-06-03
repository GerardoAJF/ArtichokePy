import abc
from artichokepy import Graph, Node
from artichokepy.graph import Relation


class Frontier:
    def __init__(self) -> None:
        self.frontier = []
        
    def get_len(self):
        return len(self.frontier)
    
    abc.abstractmethod
    def add_node(self, node: Node):
        pass
    
    abc.abstractmethod
    def remove_node(self) -> Node:
        return Node("")


class StackFrontier(Frontier):
    def add_node(self, node: Node):
        self.frontier.append(node)
        
    def remove_node(self) -> Node:
        return self.frontier.pop()


class QueueFrontier(Frontier):
    def add_node(self, node: Node):
        self.frontier.append(node)
        
    def remove_node(self) -> Node:
        return self.frontier.pop(0)

# * ===============================


class SearchAlgorithm:
    def __init__(self, frontier: Frontier) -> None:
        self.frontier = frontier
        self.exploration_set = set()

    def get_next_nodes(self, node: Node) -> set[Relation]:
        return set(node.relations)

    def search(self, graph: Graph, start: Node, end: Node):

        self.frontier.add_node(start)

        while(self.frontier.get_len() != 0 and len(self.exploration_set) != len(graph.nodes)):

            actual_node = self.frontier.remove_node()

            if actual_node == end:
                print(actual_node)
                print("Encontramos la respuesta!!!")
                break

            for relation in self.get_next_nodes(actual_node):
                if relation.end not in self.exploration_set:
                    self.frontier.add_node(relation.end)
                    self.exploration_set.add(relation.end)
