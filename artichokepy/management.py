from artichokepy import Graph, Node
import ast
import typing as t


# TODO: Que pasa si el valor tiene ; o |
class Exporter:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def to_csv(self, file_name: str):
        if file_name.endswith(".csv"):
            file_name.removesuffix(".csv")

        with open(f"{file_name}_nodes.csv", "w") as file:
            for node in self.graph.nodes:
                attributes = ""
                for key, value in node.attributes.items():
                    attributes += f"|{key};{value};{type(value).__name__}"

                node_info = f"{node._id};{node.value};{type(node.value).__name__}"
                file.write(f"{node_info}{attributes}\n")

        with open(f"{file_name}_relations.csv", "w") as file:
            for node in self.graph.nodes:
                for relation in node.relations:
                    file.write(
                        f"{relation.init._id}|{relation.end._id}|{relation.weight}\n"
                    )


class Importer:

    def parser(self, value: str, type: str) -> t.Any:
        # TODO: Hacer q el parser pueda recibir ciertas clases y no de error tan facilmente

        if type == "str":
            return value

        ast.literal_eval(value)

    def nodes_from_csv(self, file_name: str) -> t.Tuple[Graph, t.Dict[str, Node]]:
        if not file_name.endswith("_nodes.csv"):
            file_name += "_nodes.csv"

        graph = Graph()
        nodes = dict()
        with open(file_name, "r") as file:
            for line in file.readlines():
                columns = line.strip().split("|")

                node_id, node_value, node_value_type = columns[0].split(";")

                attributes = dict()
                for attribute in columns[1:]:
                    if not attribute:
                        continue

                    attr_name, attr_value, attr_value_type = attribute.split(";")
                    attributes[attr_name] = self.parser(attr_value, attr_value_type)

                node = Node(self.parser(node_value, node_value_type))
                node._id = node_id
                nodes[node_id] = graph.add_node(node)[0]

        return graph, nodes

    def relations_from_csv(self, file_name: str, nodes: t.Dict[str, Node]) -> None:
        if not file_name.endswith("_relations.csv"):
            file_name += "_relations.csv"

        with open(file_name, "r") as file:
            for line in file.readlines():
                columns = line.strip().split("|")

                init, end, weight = columns
                nodes[init].add_relation((nodes[end], float(weight)))
