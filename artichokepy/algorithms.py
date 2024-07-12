import math
import abc
import typing as t

from artichokepy.graph import Graph, Node, Relation, RelationType

NodeSolutionType = t.Tuple[Node, t.List[RelationType]]  # TODO: make this a object


# * ===============UNINFORMED FRONTIERS===============


class Frontier(abc.ABC):
    def __init__(self) -> None:
        self.frontier = []

    def clear(self) -> None:
        self.frontier.clear()

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


# * ===============FUNCTIONS===============


class CostFunction:
    def __init__(self) -> None:
        self._function: t.Callable[[NodeSolutionType], float] = lambda x: 0

    def set_function(self, function: t.Callable[[NodeSolutionType], float]) -> None:
        self._function = function

    def __call__(self, node: NodeSolutionType) -> float:
        return self._function(node)


class PathCost(CostFunction):
    def __init__(self) -> None:
        super().__init__()

        def path_length(node_solution: NodeSolutionType):
            return sum([node[1] for node in node_solution[1]])

        self.set_function(path_length)


class HeuristicFunction(CostFunction):
    def check_scale(self, graph: Graph) -> float:
        difference_sum = 0
        count = 0

        for relation in graph.relations:
            weight = relation.weight if (relation.weight != 0) else 1
            heuristic = self(
                (
                    relation.end,
                    [
                        (relation.init, relation.weight),
                    ],
                )
            )

            if heuristic == weight:
                return 0.0

            relative_diff = abs(math.log10(heuristic / weight))

            sensitivity_factor = 1.5
            scaled_diff = relative_diff / sensitivity_factor

            difference = math.tanh(scaled_diff)

            difference_sum += difference
            count += 1

        if count > 0:
            return difference_sum / count
        return 0

    def is_admissible(
        self,
        graph: Graph,
        check_nodes: t.Optional[t.Iterable[Node]] = None,
        cost: CostFunction = PathCost()
    ) -> bool:

        if not check_nodes:
            check_nodes = graph.nodes

        search = SearchAlgorithm(BFSFrontier())
        for init in check_nodes:
            for end in check_nodes:

                solution = search.search(graph, init, end)

                if not solution[1]:
                    continue

                if cost(solution) < self(solution):
                    return False
        return True


# * ==============================


class AutoSortFrontier(Frontier):
    def __init__(self, func: t.Callable[[NodeSolutionType], float]) -> None:
        super().__init__()
        self.func = func

    def ordered_index(
        self,
        node: NodeSolutionType,
        arr: t.List[NodeSolutionType],
        pointer: int = 0,
    ) -> int:

        if not arr:
            return pointer

        mid_index = (len(arr) - 1) // 2
        index = mid_index + pointer

        cost = self.func(node)

        if cost > self.func(arr[mid_index]):
            return self.ordered_index(node, arr[mid_index + 1 :], index + 1)

        elif cost < self.func(self.frontier[mid_index]):
            return self.ordered_index(node, arr[:mid_index], pointer)

        return index

    def add_node(self, node: NodeSolutionType) -> None:
        index = self.ordered_index(node, self.frontier)
        self.frontier.insert(index, node)


class DijkstraFrontier(AutoSortFrontier):
    def __init__(self, cost: CostFunction = PathCost()) -> None:
        super().__init__(cost)


class GreedyFrontier(AutoSortFrontier):
    def __init__(self, heuristic: HeuristicFunction) -> None:
        super().__init__(heuristic)


class AStarFrontier(AutoSortFrontier):
    def __init__(self, cost: CostFunction, heuristic: HeuristicFunction) -> None:

        def cost_heuristic(node_solution: NodeSolutionType):
            return cost(node_solution) + heuristic(node_solution)

        total_heuristic = HeuristicFunction()            
        total_heuristic.set_function(cost_heuristic)

        super().__init__(total_heuristic)


# * ===============GENERIC SEARCH===============


class SearchAlgorithm:
    def __init__(self, frontier: Frontier) -> None:
        self.frontier = frontier
        self.exploration_set = set()

    def reset(self):
        self.frontier.clear()
        self.exploration_set.clear()

    def get_next_nodes(self, node: Node) -> t.Set[Relation]:
        return set(node.relations)

    def search(self, graph: Graph, start: Node, end: Node) -> NodeSolutionType:
        self.reset()

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
