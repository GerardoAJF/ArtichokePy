from artichokepy import *

a = Node("a")
b = Node("b")
c = Node("c")
d = Node("d")
e = Node("e")

a.bidirectional_relation((b, 0), (c, 0))
c.bidirectional_relation((e, 0))
b.bidirectional_relation((d, 0))

my_graph = Graph()
my_graph.add_node(a, b, c, d, e)

my_graph.print_adjacent_matrix()

search = SearchAlgorithm(StackFrontier())

search.search(my_graph, a, d)
