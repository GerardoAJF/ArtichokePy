import typing as t
import colorama as cl
import itertools as tools


RelationType = t.Tuple["Node", float]
MatrixType = t.Iterable[t.Iterable[t.Any]]

class Node:
    def __init__(self, value: t.Any) -> None:
        self.value = value
        self.degree = 0
        self.relations: t.Set[Relation] = set()
        self.graphs = set()

    def __repr__(self) -> str:
        return str(self.value)

    def bidirectional_relation(self, *relations: RelationType) -> t.Self:
        for node, weight in relations:
            relation = Relation(self, node, weight)

            self.relations.add(relation)
            node.relations.add(relation.reverse())

        self.update_degree()
        self.notify_update()
        return self

    def unidirectional_relation(self, *relations: RelationType) -> t.Self:
        for node, weight in relations:
            self.relations.add(Relation(self, node, weight))

        self.update_degree()
        self.notify_update()
        return self

    def add_graph(self, graph) -> t.Self:
        self.graphs.add(graph)
        return self

    def remove_graph(self, graph) -> t.Self:
        self.graphs.discard(graph)
        return self

    def update_degree(self) -> None:
        self.degree = len(self.relations)
        
    def is_child(self, parent: "Node"):
        for relation in parent.relations:
            if relation.end == self:
                return True
        return False

    def notify_update(self) -> None:
        for graph in self.graphs:
            graph.notify_update()


class Relation:
    def __init__(self, init: Node, end: Node, weight: float = 0) -> None:
        self.init = init
        self.end = end

        self.weight = weight
    
    def __repr__(self) -> str:
        return f"{str(self.init)} -> {str(self.end)}: {self.weight}"

    def reverse(self) -> "Relation":
        return Relation(self.end, self.init, self.weight)

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Relation):
            if (self.weight == value.weight) and (self.init is value.init) and (self.end is value.end):
                return True
        return False
    
    def __hash__(self) -> int:
        return hash((self.weight, self.init, self.end))


class Graph:
    def __init__(self) -> None:
        self._nodes = set()
        self.adjacent_matrix = [[]]
        self._id = tools.count()

    # * NODES-------------------------------------

    @property
    def nodes(self) -> t.Set[Node]:
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: t.Iterable[Node]):
        for node in nodes:
            self._nodes.add(node)
            node.add_graph(self)

        self.update_adjacent_matrix()

    def add_node(self, *values: t.Any) -> t.Iterable[Node]:
        nodes = []
        for value in values: 
            node = Node(value)
            nodes.append(node)

            self._nodes.add(node)
            node.add_graph(self)

        self.update_adjacent_matrix()

        if len(nodes) == 1:
            return nodes[0]
        return nodes

    def remove_node(self, *nodes: Node) -> None:
        for node in nodes:
            self.nodes.discard(node)
            node.remove_graph(self)

            for old_node in self.nodes:
                for relation in old_node.relations.copy():
                    if relation.end == node:
                        old_node.relations.discard(relation)

        self.update_adjacent_matrix()

    # * ADJACENT MATRIX-------------------------------------

    def create_adjacent_matrix(self) -> MatrixType:
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

    def update_adjacent_matrix(self) -> None:
        self.adjacent_matrix = self.create_adjacent_matrix()

    # * TYPES-------------------------------------

    def is_eulerian(self) -> bool:
        odd_nodes = 0

        for node in self.nodes:
            if node.degree % 2 == 1:
                odd_nodes += 1

        if (odd_nodes == 0) or (odd_nodes == 2):
            return True
        return False

    # * OPERATORS-------------------------------------

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Graph):
            return self.adjacent_matrix == value.adjacent_matrix
        return False

    def __hash__(self) -> int:
        return hash(((value for fila in self.adjacent_matrix for value in fila), self._id))

    def __add__(self, graph: t.Self) -> "Graph":
        new_graph = Graph()
        new_graph.nodes = self.nodes.union(graph.nodes)

        return new_graph

    def __sub__(self, graph: t.Self) -> "Graph":
        new_graph = Graph()
        new_graph.nodes = self.nodes.difference(graph.nodes)

        return new_graph

    # * OTHERS-------------------------------------

    def notify_update(self) -> None:
        self.update_adjacent_matrix()


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
    my_graph = Graph()

    a, b, c, d = my_graph.add_node("A", "B", "C", "D")
