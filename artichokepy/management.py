from artichokepy.graph import Graph, Node
import ast
import typing as t

class CustomValue:
    def csv_printer(self) -> str:
        params = ""
        for key, value in vars(self).items():
            params += f"{key}{CsvDocument.signs["arg_sign"]}{CsvDocument.csv_printer(value)}{CsvDocument.signs["param_sign"]}"

        return f"({params}){CsvDocument.signs["arg_sign"]}{self.__class__.__name__}"

    @classmethod
    def csv_parser(cls, value: str) -> t.Self:
        value = value[1:-1]
        params = dict()

        for parameter in CsvDocument.param_splitter(value):
            if not parameter:
                continue

            param = parameter.split(CsvDocument.signs["arg_sign"])
            param_name = param[0]
            param_type = param[-1]
            param_value = CsvDocument.signs["arg_sign"].join(param[1:-1])

            params[param_name] = CsvDocument.csv_parser(param_value, param_type)

        return cls.constructor(**params)

    def json_printer(self) -> t.Dict[str, t.Any]:
        params: t.Dict[str, t.Any] = {"__type": self.__class__.__name__}

        for key, value in vars(self).items():
            params[key] = JsonDocument.json_printer(value)

        return params

    @classmethod
    def json_parser(cls, value: t.Dict[str, t.Any]) -> t.Self:
        params = dict()
        for param_name in value.keys():
            if param_name == "__type":
                continue

            params[param_name] = JsonDocument.json_parser(value[param_name])

        return cls.constructor(**params)

    @classmethod
    def constructor(cls, **kwargs) -> t.Self:
        return cls(**kwargs)


class CsvDocument:
    signs = {"node_sign": ";", "attr_sign": "$", "param_sign": "\\", "arg_sign": "|"}

    @classmethod
    def csv_parser(cls, value: str, type_: str) -> t.Any:
        if type_ == "str":
            return value

        for custom_value in CustomValue.__subclasses__():
            if type_ == custom_value.__name__:
                return custom_value.csv_parser(value)

        return ast.literal_eval(value)

    @classmethod
    def csv_printer(cls, value: t.Any):
        if isinstance(value, CustomValue):
            return value.csv_printer()

        return f"{value}{CsvDocument.signs["arg_sign"]}{type(value).__name__}"

    @staticmethod
    def param_splitter(text: str):
        open_paren = 0
        closed_paren = 0

        first_index = 0
        for last_index, char in enumerate(text):
            if char == "(":
                open_paren += 1
            elif char == ")":
                closed_paren += 1
            elif char == CsvDocument.signs["param_sign"] and open_paren == closed_paren:
                yield text[first_index:last_index]
                first_index = last_index + 1


class JsonDocument:
    @classmethod
    def json_parser(cls, value: t.Dict[str, t.Any]) -> t.Any:
        for custom_value in CustomValue.__subclasses__():
            if value["__type"] == custom_value.__name__:
                return custom_value.json_parser(value)

        return value["__value"]

    @classmethod
    def json_printer(cls, value: t.Any):
        if isinstance(value, CustomValue):
            return value.json_printer()

        return {"__value": value, "__type": type(value).__name__}

    @classmethod
    def dict_printer(cls, dict_: t.Dict[str, t.Any]):
        if isinstance(dict_, dict):
            items = [f'"{k}": {JsonDocument.dict_printer(v)}' for k, v in dict_.items()]
            return "{" + ", ".join(items) + "}"

        elif isinstance(dict_, str):
            return f'"{dict_}"'

        else:
            return str(dict_)

    @staticmethod
    def dict_splitter(text: str):
        open_bracket = 0
        closed_bracket = 0

        first_index = 0
        for last_index, char in enumerate(text):
            if char == "{":
                open_bracket += 1
            elif char == "}":
                closed_bracket += 1
            elif char == "," and open_bracket == closed_bracket:
                yield text[first_index:last_index]
                first_index = last_index + 1


class Exporter:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph

    def to_csv(self, file_name: str):
        if file_name.endswith(".csv"):
            file_name = file_name.removesuffix(".csv")

        with open(f"{file_name}_nodes.csv", "w") as file:
            for node in self.graph.nodes:
                attributes = ""
                for key, value in node.attributes.items():
                    attributes += f"{key}{CsvDocument.signs["arg_sign"]}{CsvDocument.csv_printer(value)}{CsvDocument.signs["attr_sign"]}"

                file.write(
                    f"{node._id}{CsvDocument.signs["node_sign"]}{CsvDocument.csv_printer(node.value)}{CsvDocument.signs["node_sign"]}{attributes}\n"
                )

        with open(f"{file_name}_relations.csv", "w") as file:
            for node in self.graph.nodes:
                for relation in node.relations:
                    file.write(
                        f"{relation.init._id}{CsvDocument.signs["arg_sign"]}{relation.end._id}{CsvDocument.signs["arg_sign"]}{relation.weight}\n"
                    )

    def to_json(self, file_name: str):
        if file_name.endswith(".json"):
            file_name = file_name.removesuffix(".json")

        with open(f"{file_name}_nodes.json", "w") as file:
            file.write("[")

            for node in self.graph.nodes:
                file.write(
                    JsonDocument.dict_printer(
                        {
                            "__id": node._id,
                            "__value": JsonDocument.json_printer(node.value),
                            "__attributes": {
                                key: JsonDocument.json_printer(value)
                                for key, value in node.attributes.items()
                            },
                        }
                    )
                    + ","
                )

            file.write("]")

        with open(f"{file_name}_relations.json", "w") as file:
            file.write("[")

            for node in self.graph.nodes:
                relations = dict()
                for relation in node.relations:
                    relations[relation.end._id] = relation.weight

                file.write(
                    JsonDocument.dict_printer(
                        {"__node": node._id, "__relations": relations}
                    )
                    + ", "
                )

            file.write("]")


class Importer:
    def nodes_from_csv(self, file_name: str) -> t.Tuple[Graph, t.Dict[str, Node]]:
        if not file_name.endswith("_nodes.csv"):
            file_name += "_nodes.csv"

        graph = Graph()
        nodes = dict()
        with open(file_name, "r") as file:
            for line in file.readlines():
                columns = line.strip().split(CsvDocument.signs["node_sign"])

                node_id = columns[0]

                value = columns[1].split(CsvDocument.signs["arg_sign"])
                node_value_type = value[-1]
                node_value = CsvDocument.signs["arg_sign"].join(value[0:-1])

                attributes = dict()
                for attribute in columns[2].split(CsvDocument.signs["attr_sign"]):
                    if not attribute:
                        continue

                    attr = attribute.split(CsvDocument.signs["arg_sign"])
                    attr_name = attr[0]
                    attr_value_type = attr[-1]
                    attr_value = CsvDocument.signs["arg_sign"].join(attr[1:-1])

                    attributes[attr_name] = CsvDocument.csv_parser(
                        attr_value, attr_value_type
                    )

                node = Node(
                    CsvDocument.csv_parser(node_value, node_value_type), **attributes
                )
                node._id = node_id
                nodes[node_id] = graph.add_node(node)[0]

        return graph, nodes

    def relations_from_csv(self, file_name: str, nodes: t.Dict[str, Node]) -> None:
        if not file_name.endswith("_relations.csv"):
            file_name += "_relations.csv"

        with open(file_name, "r") as file:
            for line in file.readlines():
                columns = line.strip().split(CsvDocument.signs["arg_sign"])

                init, end, weight = columns
                nodes[init].add_relation((nodes[end], float(weight)))

    def nodes_from_json(self, file_name: str) -> t.Tuple[Graph, t.Dict[str, Node]]:
        if not file_name.endswith("_nodes.json"):
            file_name += "_nodes.json"

        graph = Graph()
        nodes = dict()
        with open(file_name, "r") as file:
            for dict_ in JsonDocument.dict_splitter(file.read()[1:-1]):
                node_dict = ast.literal_eval(dict_)

                node = Node(
                    JsonDocument.json_parser(node_dict["__value"]),
                    **{
                        attribute: JsonDocument.json_parser(
                            node_dict["__attributes"][attribute]
                        )
                        for attribute in node_dict["__attributes"].keys()
                    },
                )
                node._id = node_dict["__id"]
                nodes[node._id] = graph.add_node(node)[0]

            return graph, nodes

    def relations_from_json(self, file_name: str, nodes: t.Dict[str, Node]) -> None:
        if not file_name.endswith("_relations.json"):
            file_name += "_relations.json"

        with open(file_name, "r") as file:
            for dict_ in JsonDocument.dict_splitter(file.read()[1:-1]):
                node_dict = ast.literal_eval(dict_)

                for node_id, relation_weight in node_dict["__relations"].items():
                    nodes[node_dict["__node"]].add_relation(
                        (nodes[node_id], relation_weight)
                    )
