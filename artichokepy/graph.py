import typing as t
import colorama as cl


class Node:
    def __init__(self, value: t.Any) -> None:
        self.value = value
        self.relations: t.Set[Relation] = set()
        self.graphs = set()

    def __str__(self) -> str:
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

    def remove_graph(self, graph):
        self.graphs.remove(graph)

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

    def __str__(self) -> str:
        return f"{str(self.init)} -> {str(self.end)}: {self.weight}"


class Graph:
    def __init__(self) -> None:
        self._nodes = set()
        self.adjacent_matrix = [[]]

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

    def remove_node(self, node):
        self.nodes.discard(node)
        node.remove_graph(self)

        self.update_adjacent_matrix()
        return self

    def create_adjacent_matrix(self):
        index = {node: index for index, node in enumerate(self.nodes)}
        values = [node.value for node in self.nodes]

        matrix = [["@", *values]]

        for value in values:
            matrix.append([value] + [0] * len(values))

        for node in self.nodes:
            init = index[node]
            for relation in node.relations:
                if relation.end in index:
                    end = index[relation.end]
                    matrix[init + 1][end + 1] = 1

        return matrix

    def update_adjacent_matrix(self):
        self.adjacent_matrix = self.create_adjacent_matrix()

    def print_adjacent_matrix(self) -> None:
        cl.init(autoreset=True)

        colors = {0: cl.Fore.RED, 1: cl.Fore.GREEN}

        for line in self.adjacent_matrix:
            for column in line:
                color = colors.get(column, cl.Fore.LIGHTWHITE_EX)

                print(color + str(column), end=" | ")

            print()

    def notify_update(self):
        self.update_adjacent_matrix()


if __name__ == "__main__":
    a = Node("A")
    b = Node("B")
    c = Node("C").bidirectional_relation((b, 0)).unidirectional_relation((a, 0))
    d = Node("D").unidirectional_relation((a, 0))

    graph1 = Graph()
    graph1.add_node(a, b, c, d)
