import typing as t
import colorama as cl
import itertools as tools

RelationType = t.Tuple["Node", float]

VectorType = t.Dict["Node", t.Any]
MatrixType = t.Dict["Node", VectorType]

class Node:
    counter = tools.count()

    def __init__(self, value: t.Any) -> None:
        self._id = "N" + str(next(Node.counter))
        self.value = value

        self.parents: t.Set["Node"] = set()
        self.relations: t.Set[Relation] = set()

    def __repr__(self) -> str:
        return str(self.value)

    @property
    def degree(self) -> int:
        return len(self.relations)

    def add_relation(self, *relations: RelationType, bidirectional=False) -> t.Self:
        for node, weight in relations:
            relation = Relation(self, node, weight)
            self.relations.add(relation)
            node.parents.add(self)

            if bidirectional:
                node.relations.add(relation.reverse())
                self.parents.add(node)

        return self

    def remove_relation(self, *nodes: "Node", bidirectional=False) -> t.Self:        
        for relation in self.relations.copy():
            if relation.end in nodes:
                self.relations.discard(relation)
                relation.end.parents.discard(self)

                if bidirectional:
                    relation.end.relations.discard(relation.reverse())
                    self.parents.discard(relation.end)
        
        return self

    def __eq__(self, value: object) -> bool:
        if isinstance(value, Node) and (self._id == value._id):
            return True
        return False

    def __hash__(self) -> int:
        return hash(self._id)


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
            if (self.weight == value.weight) and (self.init == value.init) and (self.end == value.end):
                return True
        return False
    
    def __hash__(self) -> int:
        return hash((self.weight, self.init, self.end))


class Graph:
    counter = tools.count()

    def __init__(self) -> None:
        self._id = "G" + str(next(Graph.counter))
        self.nodes = set()

    # * NODES-------------------------------------

    def add_node(self, *nodes: t.Union[Node, t.Any]) -> t.List[Node]:
        new_nodes = []

        for node in nodes:

            if isinstance(node, Node):
                new_node = Node(node.value)
                new_node._id = node._id

            else:
                new_node = Node(node)

            new_nodes.append(new_node)
            self.nodes.add(new_node)

        return new_nodes

    def remove_node(self, *nodes: Node) -> None:
        for node in nodes:
            self.nodes.discard(node)

            for parent in node.parents.copy():
                parent.remove_relation(node)

    @property
    def relations(self) -> t.Set[Relation]:
        relations = set()

        for node in self.nodes:
            relations.update(node.relations)

        return relations

    @relations.setter
    def relations(self, relations: t.Set[Relation]) -> None:        
        nodes_converter = dict()

        for relation in relations:
            old_init = relation.init
            old_end = relation.end

            if old_init not in nodes_converter:
                nodes_converter[old_init] = self.add_node(old_init)[0]

            if old_end not in nodes_converter:
                nodes_converter[old_end] = self.add_node(old_end)[0]

            init_node = nodes_converter[old_init]
            end_node = nodes_converter[old_end]

            init_node.add_relation((end_node, relation.weight))

    @property
    def adjacency_matrix(self) -> MatrixType:
        matrix = {node: {node: 0 for node in self.nodes} for node in self.nodes}

        for relation in self.relations:
            matrix[relation.init][relation.end] = 1

        return matrix

    @property
    def adjacency_list(self) -> VectorType:
        adjacency_list = dict()

        for node in self.nodes:
            adjacency_list[node] = []

            for relation in node.relations:
                adjacency_list[node].append(relation.end)

        return adjacency_list

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
            return [[*row.values()] for row in self.adjacency_matrix.values()] == [
                    [*row.values()] for row in value.adjacency_matrix.values()]
        return False

    def __hash__(self) -> int:
        return hash((([*row.values()] for row in self.adjacency_matrix.values()), self._id))

    def __add__(self, graph: t.Self) -> "Graph": 
        new_graph = Graph()
        new_graph.relations = self.relations.union(graph.relations);

        return new_graph

    def __sub__(self, graph: t.Self) -> "Graph": 
        new_graph = Graph()  
        new_graph.relations = self.relations.difference(graph.relations);

        return new_graph


def print_adjacent_matrix(matrix: t.Union[Graph, MatrixType]) -> None:
    cl.init(autoreset=True)
    colors = {0: cl.Fore.RED, 1: cl.Fore.GREEN}
    
    if isinstance(matrix, Graph):
        matrix = matrix.adjacency_matrix
    
    print("@", *matrix)
    
    for node, row in matrix.items():
        print(str(node), end=" ")
        for number in row.values():
            print(colors.get(number, cl.Fore.WHITE) + str(number), end=" ")
        print()
    
    print(cl.Fore.YELLOW + "-" * 25)


if __name__ == "__main__":
    my_graph = Graph()
    a, b, c = my_graph.add_node("A", "B", "C")

    a.add_relation((b, 0), (c, 0))
    print_adjacent_matrix(my_graph)
   
    my_graph2 = Graph()
    a2, c2, d = my_graph2.add_node(a, c, "D")
    
    c2.add_relation((a2, 0), (d, 0))
    print_adjacent_matrix(my_graph2)

    print_adjacent_matrix(my_graph + my_graph2)
    print_adjacent_matrix(my_graph - my_graph2)
