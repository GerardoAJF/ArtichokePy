import abc
import typing as t
from artichokepy.graph import Graph, Node, Relation

NodeSolutionType = t.Tuple[Node, t.List[t.Tuple[Node, float]]]

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
    def add_node(self, node: NodeSolutionType) -> None:
        self.frontier.insert(self.get_index(self.frontier, node), node)

    def get_index(self, arr: t.List[NodeSolutionType], node: NodeSolutionType, pointer: int = 0) -> int:        
        if len(arr) == 0:
            return pointer

        average_index = (len(arr) - 1) // 2
        index = average_index + pointer

        path_value = self.get_path_value(node)
        if path_value > self.get_path_value(arr[average_index]):
            return self.get_index(arr[average_index + 1 :], node, index + 1)

        elif path_value < self.get_path_value(arr[average_index]):
            return self.get_index(arr[0:average_index], node, pointer)

        return index

    def get_path_value(self, node: NodeSolutionType) -> float:
        return sum((parent[1] for parent in node[1]))

    def remove_node(self) -> NodeSolutionType:
        return self.frontier.pop(0)


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
                    self.frontier.add_node((relation.end, [(actual_node[0], relation.weight)] + actual_node[1]))
                
        return (Node(""), [])

if __name__ == "__main__":
    dijkstra = DijkstraFrontier() 

    none = Node("")

    a = Node("a")
    b = Node("b")
    c = Node("c")
    d = Node("d")
    e = Node("e")

    dijkstra.add_node((a, [(none, -1.0)]))
    dijkstra.add_node((b, [(none, 5.0), (none, -7.0)]))
    dijkstra.add_node((c, [(none, 7.0)]))
    dijkstra.add_node((d, [(none, 8.0)]))
    dijkstra.add_node((e, [(none, 4.0)]))    

    print(dijkstra.frontier)
