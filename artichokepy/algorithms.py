import math
import abc
import typing as t
import functools

from artichokepy.graph import Graph, Node, Relation


class NodeSolution:
    def __init__(self, node: Node) -> None:
        self.node = node

        self.path = []

    def __repr__(self) -> str:
        return f"{self.node} :: {' & '.join(str(relation) for relation in self.path)}"

    def add_steps(self, *relations: Relation) -> t.Self:
        for relation in relations:
            self.path.append(relation)
        return self

    def get_previous_node(self, step=1) -> Node:
        if len(self.path) < step:
            step = 0

        return self.path[-step].init

    def __eq__(self, value: object) -> bool:
        if isinstance(value, NodeSolution):
            return self.node == value.node and self.path == value.path
        return False

    def __hash__(self) -> int:
        return hash((self.node, *self.path))


# * ===============UNINFORMED FRONTIERS===============


class Frontier(abc.ABC):
    def __init__(self) -> None:
        self.frontier = []

    def clear(self) -> None:
        self.frontier.clear()

    def get_len(self) -> int:
        return len(self.frontier)

    @abc.abstractmethod
    def add_node(self, node: NodeSolution) -> None:
        pass

    def remove_node(self) -> NodeSolution:
        return self.frontier.pop(0)


class DFSFrontier(Frontier):
    def add_node(self, node: NodeSolution) -> None:
        self.frontier.append(node)

    def remove_node(self) -> NodeSolution:
        return self.frontier.pop()


class BFSFrontier(Frontier):
    def add_node(self, node: NodeSolution) -> None:
        self.frontier.append(node)


# * ===============FUNCTIONS===============


class CostFunction:
    def __init__(self) -> None:
        self._function: t.Callable[[NodeSolution], float] = lambda x: 0

    def set_function(self, function: t.Callable[[NodeSolution], float]) -> None:
        self._function = function

    def __call__(self, node: NodeSolution) -> float:
        return self._function(node)


class PathCost(CostFunction):
    def __init__(self) -> None:
        super().__init__()

        def path_length(node_solution: NodeSolution):
            return sum([relation.weight for relation in node_solution.path])

        self.set_function(path_length)


class State:
    def __init__(self, value: t.Any) -> None:
        self.value: t.Any = value
        self.update_func = lambda : self.value

    def add_update_func(self, func: t.Callable, **arguments):
        if arguments:
            self.update_func = lambda: func(**arguments)
            return 

        self.update_func = func

    def _update_value(self):
        self.value = self.update_func()


class HeuristicFunction(CostFunction):
    def __init__(self) -> None:
        super().__init__()

        self.states: t.Dict[str, State] = {}

    def add_state(self, *values: t.Tuple[str, t.Any]):
        new_states = []
        for value in values:
            state = State(value[1])

            new_states.append(state)
            self.states[value[0]] = state

        return new_states

    def subscribe_state(self, *states: t.Union[str, State]):
        def decorator(func: t.Callable):

            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                x = func(*args, **kwargs)
                for state in states:
                    if not (state in self.states.keys() or state in self.states.values()):
                        continue

                    if isinstance(state, str):
                        state = self.states[state]

                    state._update_value()
                return x

            return wrapper
        return decorator

    def __get_paths(
        self, graph: Graph, check_nodes: t.Optional[t.Iterable[Node]]
    ) -> t.List[NodeSolution]:

        if not check_nodes:
            check_nodes = graph.nodes

        solutions = []

        search = SearchAlgorithm(BFSFrontier())
        for init in check_nodes:
            for end in check_nodes:

                solution = search.search(graph, init, end)

                # There is no point in checking nodes that are disconnected.
                if not solution.path:
                    continue

                solutions.append(solution)

        return solutions

    def check_scale(
        self,
        graph: Graph,
        cost: CostFunction = PathCost(),
        check_nodes: t.Optional[t.Iterable[Node]] = None,
    ) -> float:

        count = 0
        value = 0

        for solution in self.__get_paths(graph, check_nodes):

            cost_value = cost(solution)
            heuristic_value = self(solution)

            if cost_value == 0 or heuristic_value == 0:
                continue

            difference = heuristic_value / cost_value
            if cost_value > heuristic_value:
                difference = cost_value / heuristic_value
                difference = 1 - (difference - 1)

            # sigmoid function shifted one to the right
            sig = 1 / (1 + math.exp(-0.04605 * (difference - 1)))

            count += 1
            value += sig

        if count:
            return value / count
        return 0.5

    def is_admissible(
        self,
        graph: Graph,
        cost: CostFunction = PathCost(),
        check_nodes: t.Optional[t.Iterable[Node]] = None,
    ) -> bool:

        for solution in self.__get_paths(graph, check_nodes):
            if cost(solution) < self(solution):
                return False

        return True

    def is_consistent(
        self,
        graph: Graph,
        cost: CostFunction = PathCost(),
        check_nodes: t.Optional[t.Iterable[Node]] = None,
    ) -> bool:

        paths = self.__get_paths(graph, check_nodes)
        nodes = {solution.node: solution for solution in paths}

        for solution in paths:
            prev_node = solution.get_previous_node(0)
            prev_solution = nodes.get(prev_node, NodeSolution(prev_node))

            if self(prev_solution) > cost(solution) + self(solution):
                return False

        return True


# * ==============="INFORMED" FRONTIERS===============


class AutoSortFrontier(Frontier):
    def __init__(self, func: t.Callable[[NodeSolution], float]) -> None:
        super().__init__()
        self.func = func

    def __ordered_index(
        self,
        node: NodeSolution,
        arr: t.List[NodeSolution],
        pointer: int = 0,
    ) -> int:

        if not arr:
            return pointer

        mid_index = (len(arr) - 1) // 2
        index = mid_index + pointer

        cost = self.func(node)

        if cost > self.func(arr[mid_index]):
            return self.__ordered_index(node, arr[mid_index + 1 :], index + 1)

        elif cost < self.func(arr[mid_index]):
            return self.__ordered_index(node, arr[:mid_index], pointer)

        return index

    def add_node(self, node: NodeSolution) -> None:
        index = self.__ordered_index(node, self.frontier)
        self.frontier.insert(index, node)


class DijkstraFrontier(AutoSortFrontier):
    def __init__(self, cost: CostFunction = PathCost()) -> None:
        super().__init__(cost)


class GreedyFrontier(AutoSortFrontier):
    def __init__(self, heuristic: HeuristicFunction) -> None:
        super().__init__(heuristic)


class AStarFrontier(AutoSortFrontier):
    def __init__(self, cost: CostFunction, heuristic: HeuristicFunction) -> None:

        def cost_heuristic(node_solution: NodeSolution):
            return cost(node_solution) + heuristic(node_solution)

        total_heuristic = HeuristicFunction()
        total_heuristic.set_function(cost_heuristic)

        super().__init__(total_heuristic)


# * ===============GENERIC SEARCH===============


class SearchAlgorithm:
    def __init__(self, frontier: Frontier) -> None:
        self.frontier = frontier
        self.exploration_set: t.Set[Node] = set()

    def reset(self):
        self.frontier.clear()
        self.exploration_set.clear()

    def get_next_nodes(self, node: Node) -> t.Set[Relation]:
        return set(node.relations)

    def search(self, graph: Graph, start: Node, end: Node) -> NodeSolution:
        self.reset()

        self.frontier.add_node(NodeSolution(start))
        self.exploration_set.add(start)

        while self.frontier.get_len() != 0 and len(self.exploration_set) != len(
            graph.nodes
        ):

            actual_node = self.frontier.remove_node()
            self.exploration_set.add(actual_node.node)

            if actual_node.node == end:
                return actual_node

            for relation in self.get_next_nodes(actual_node.node):
                if relation.end not in self.exploration_set:
                    self.frontier.add_node(
                        NodeSolution(relation.end).add_steps(
                            *actual_node.path, relation
                        )
                    )

        return NodeSolution(Node(None))


if __name__ == "__main__":
    pass
