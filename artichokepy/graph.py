import typing as t
import colorama as cl
import itertools as tools


class Node:
    def __init__(self, value: t.Any) -> None:
        self.value = value
        self.relations: t.Set[Relation] = set()
        self.graphs = set()

    def __repr__(self) -> str:
        return str(self.value)

    def bidirectional_relation(self, *args: t.Tuple[t.Self, float]) -> t.Self:
        for node, weight in args:
            self.relations.add(Relation(self, node, weight))
            node.relations.add(Relation(node, self, weight))

        self.notify_update()
        return self

    def unidirectional_relation(self, *args: t.Tuple[t.Self, float]) -> t.Self:
        for node, weight in args:
            self.relations.add(Relation(self, node, weight))

        self.notify_update()
        return self

    def add_graph(self, graph):
        self.graphs.add(graph)
        return self

    def remove_graph(self, graph):
        self.graphs.remove(graph)
        return self

    def notify_update(self):
        for graph in self.graphs:
            graph.notify_update()


class Relation:
    def __init__(self, init: Node, end: Node, weight: float = 0) -> None:
        self.init = init
        self.end = end

        self.weight = weight

    def reverse(self) -> "Relation":
        return Relation(self.end, self.init, self.weight)

    def __repr__(self) -> str:
        return f"{str(self.init)} -> {str(self.end)}: {self.weight}"


class Graph:
    def __init__(self) -> None:
        self._nodes = set()
        self.adjacent_matrix = [[]]
        self._id = tools.count()

    @property
    def nodes(self) -> t.Set[Node]:
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: t.Iterable[Node]):
        for node in nodes:
            self._nodes.add(node)
            node.add_graph(self)

        self.update_adjacent_matrix()

    def add_node(self, *args: Node):
        for node in args:
            self._nodes.add(node)
            node.add_graph(self)

        self.update_adjacent_matrix()
        return self

    def remove_node(self, node: Node):
        if self in node.graphs:
            self.nodes.discard(node)
            node.remove_graph(self)

            self.update_adjacent_matrix()
            return self

    def create_adjacent_matrix(self):
        nodes_index = {node: index for index, node in enumerate(self.nodes)}

        matrix = [["@", *nodes_index.keys()]]

        for node in nodes_index.keys():
            matrix.append([node] + [0] * len(nodes_index))

        for node in self.nodes:
            init = nodes_index[node]
            for relation in node.relations:
                if relation.end in nodes_index:
                    end = nodes_index[relation.end]
                    matrix[init + 1][end + 1] = 1

        return matrix

    def update_adjacent_matrix(self):
        self.adjacent_matrix = self.create_adjacent_matrix()

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Graph):
            return self.adjacent_matrix == value.adjacent_matrix
        return False

    def __hash__(self) -> int:
        return hash(((value for fila in self.adjacent_matrix for value in fila), self._id))

    def __add__(self, graph: t.Self):
        new_graph = Graph()
        new_graph.nodes = self.nodes.union(graph.nodes)

        return new_graph

    def __sub__(self, graph: t.Self):
        new_graph = Graph()
        new_graph.nodes = self.nodes.difference(graph.nodes)
        
        return new_graph

    def notify_update(self):
        self.update_adjacent_matrix()


MatrixType = t.Iterable[t.Iterable[t.Any]]


def print_adjacent_matrix(graph: t.Union[Graph, MatrixType]) -> None:
    cl.init(autoreset=True)
    colors = {0: cl.Fore.RED, 1: cl.Fore.GREEN}

    if isinstance(graph, Graph):
        graph = graph.adjacent_matrix

    for line in graph:
        for column in line:
            color = colors.get(column, cl.Fore.LIGHTWHITE_EX)
            print(color + str(column), end=" | ")
        print()


if __name__ == "__main__":
    a = Node("A")
    b = Node("B")
    c = Node("C").bidirectional_relation((b, 0)).unidirectional_relation((a, 0))
    d = Node("D").unidirectional_relation((a, 0))

    graph1 = Graph()
    graph1.add_node(a, b, c)

    graph2 = Graph()
    graph2.add_node(a, d)

    print_adjacent_matrix(graph1)
    print("-"*10)

    print_adjacent_matrix(graph2)
    print("-" * 10)

    print_adjacent_matrix(graph1 + graph2)
    print("-"*10)
