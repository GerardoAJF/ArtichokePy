import abc
import typing as t
from artichokepy.graph import Graph, Node, Relation

NodeSolutionType = t.Tuple[Node, t.List[t.Tuple[Node, float]]]


class OrderedList:

    @staticmethod
    def ordered_index(
        arr: t.List[NodeSolutionType],
        node: NodeSolutionType,
        function: t.Callable[[NodeSolutionType], float],
        pointer: int = 0,
    ) -> int:
        if not arr:
            return pointer

        mid_index = (len(arr) - 1) // 2
        index = mid_index + pointer
        path_value = function(node)

        if path_value > function(arr[mid_index]):
            return OrderedList.ordered_index(
                arr[mid_index + 1 :], node, function, index + 1
            )
        elif path_value < function(arr[mid_index]):
            return OrderedList.ordered_index(arr[:mid_index], node, function, pointer)

        return index

    @staticmethod
    def insert_ordered(
        arr: t.List[NodeSolutionType],
        node: NodeSolutionType,
        function: t.Callable[[NodeSolutionType], float],
    ) -> None:
        
        index = OrderedList.ordered_index(arr, node, function)
        arr.insert(index, node)

# * ===============UNINFORMED FRONTIERS===============

class Frontier(abc.ABC):
    def __init__(self) -> None:
        self.frontier = []

    def get_len(self) -> int:
        return len(self.frontier)

    @abc.abstractmethod
    def add_node(self, node: NodeSolutionType) -> None:
        pass

    def remove_node(self) -> NodeSolutionType:
        return self.frontier.pop(0)


class DFSFrontier(Frontier):
    def add_node(self, node: NodeSolutionType) -> None:
        self.frontier.append(node)

    def remove_node(self) -> NodeSolutionType:
        return self.frontier.pop()


class BFSFrontier(Frontier):
    def add_node(self, node: NodeSolutionType) -> None:
        self.frontier.append(node)


class DijkstraFrontier(Frontier):
    def add_node(self, node: NodeSolutionType) -> None:
        OrderedList.insert_ordered(self.frontier, node, self.get_path_value)
       

    def get_path_value(self, node: NodeSolutionType) -> float:
        return sum((parent[1] for parent in node[1]))

# * ===============INFORMED FRONTIERS===============

class HeuristicFunction:
    def __init__(self) -> None:
        self.previous_node_solution = (Node(""), [()])
        self.node_solution = (Node(""), [()])

        self.function: t.Callable[[NodeSolutionType], float] = lambda x: 0

    @property
    def previous_node(self):
        return self.previous_node_solution[0]

    @property
    def node(self):
        return self.node_solution[0]

    def set_function(self, function: t.Callable[[NodeSolutionType], float]):
        self.function = function

    def __call__(self, node: NodeSolutionType) -> float:
        if not self.previous_node.value:
            self.previous_node_solution = node

        self.node_solution = node
        value = self.function(node)
        self.previous_node_solution = self.node_solution
        
        return value


class GreedyFrontier(Frontier):
    def __init__(self) -> None:
        super().__init__()
        self.heuristic = HeuristicFunction()

    def set_heuristic(self, heuristic: HeuristicFunction) -> None:
        self.heuristic = heuristic

    def add_node(self, node: NodeSolutionType) -> None:
        OrderedList.insert_ordered(self.frontier, node, self.heuristic)

# * ===============GENERIC SEARCH===============


class SearchAlgorithm:
    def __init__(self, frontier: Frontier) -> None:
        self.frontier = frontier
        self.exploration_set = set()

    def get_next_nodes(self, node: Node) -> set[Relation]:
        return set(node.relations)

    def search(self, graph: Graph, start: Node, end: Node) -> NodeSolutionType:
        self.frontier.add_node((start, []))
        self.exploration_set.add(start)

        while self.frontier.get_len() != 0 and len(self.exploration_set) != len(
            graph.nodes
        ):

            actual_node = self.frontier.remove_node()
            self.exploration_set.add(actual_node[0])

            if actual_node[0] == end:
                return actual_node

            for relation in self.get_next_nodes(actual_node[0]):
                if relation.end not in self.exploration_set:
                    self.frontier.add_node(
                        (
                            relation.end,
                            [(actual_node[0], relation.weight)] + actual_node[1],
                        )
                    )

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
