import pytest
import sys
import random
import os


sys.path.append("../artichokepy")

from artichokepy.management import *
from artichokepy.algorithms import *

# *==================CUSTOM VALUE=====================


@pytest.fixture
def custom_value():
    class Coords(CustomValue):
        def __init__(self, x, y) -> None:
            self.x = x
            self.y = y
            self.random = random.randint(0, 100)

        @classmethod
        def constructor(cls, **kwargs):
            coord = Coords(kwargs["x"], kwargs["y"])
            coord.random = kwargs["random"]

            return coord

    return Coords


def test_custom_value_csv_printer(custom_value):
    coord = custom_value(1, 2)
    assert (
        coord.csv_printer() == f"(x|1|int\\y|2|int\\random|{coord.random}|int\\)|Coords"
    )


def test_custom_value_csv_parser(custom_value):
    coord1 = custom_value.csv_parser("(x|1|int\\y|2|int\\random|37|int\\)|Coords")

    coord2 = custom_value(1, 2)
    coord2.random = 37

    assert coord1.x == coord2.x
    assert coord1.y == coord2.y
    assert coord1.random == coord2.random


def test_custom_value_json_printer(custom_value):
    coord = custom_value(1, 2)
    assert coord.json_printer() == {
        "__type": "Coords",
        "x": {"__value": 1, "__type": "int"},
        "y": {"__value": 2, "__type": "int"},
        "random": {"__value": coord.random, "__type": "int"},
    }


def test_custom_value_json_parser(custom_value):
    coord1 = custom_value.json_parser(
        {
            "__type": "Coords",
            "x": {"__value": 1, "__type": "int"},
            "y": {"__value": 2, "__type": "int"},
            "random": {"__value": 37, "__type": "int"},
        }
    )

    coord2 = custom_value(1, 2)
    coord2.random = 37

    assert coord1.x == coord2.x
    assert coord1.y == coord2.y
    assert coord1.random == coord2.random


# *==================CSV DOCUMENT=====================


def test_csv_document_parser(custom_value):
    assert CsvDocument.csv_parser("3", "int") == 3
    assert CsvDocument.csv_parser("4", "str") == "4"
    assert CsvDocument.csv_parser("(1, 2)", "tuple") == (1, 2)

    coord1 = CsvDocument.csv_parser("(x|1|int\\y|2|int\\random|37|int\\)", "Coords")

    coord2 = custom_value(1, 2)
    coord2.random = 37

    assert coord1.x == coord2.x
    assert coord1.y == coord2.y
    assert coord1.random == coord2.random


def test_csv_document_printer(custom_value):
    assert CsvDocument.csv_printer(3) == "3|int"
    assert CsvDocument.csv_printer("4") == "4|str"
    assert CsvDocument.csv_printer((1, 2)) == "(1, 2)|tuple"

    coord = custom_value(1, 2)
    assert (
        CsvDocument.csv_printer(coord)
        == f"(x|1|int\\y|2|int\\random|{coord.random}|int\\)|Coords"
    )


# *==================JSON DOCUMENT=====================


def test_json_document_parser(custom_value):
    assert JsonDocument.json_parser({"__value": 3, "__type": "int"}) == 3
    assert JsonDocument.json_parser({"__value": "4", "__type": "str"}) == "4"
    assert JsonDocument.json_parser({"__value": (1, 2), "__type": "tuple"}) == (1, 2)

    coord1 = JsonDocument.json_parser(
        {
            "__type": "Coords",
            "x": {"__value": 1, "__type": "int"},
            "y": {"__value": 2, "__type": "int"},
            "random": {"__value": 37, "__type": "int"},
        }
    )

    coord2 = custom_value(1, 2)
    coord2.random = 37

    assert coord1.x == coord2.x
    assert coord1.y == coord2.y
    assert coord1.random == coord2.random


def test_json_document_printer(custom_value):
    assert JsonDocument.json_printer(3) == {"__value": 3, "__type": "int"}
    assert JsonDocument.json_printer("4") == {"__value": "4", "__type": "str"}
    assert JsonDocument.json_printer((1, 2)) == {"__value": (1, 2), "__type": "tuple"}

    coord = custom_value(1, 2)
    assert JsonDocument.json_printer(coord) == {
        "__type": "Coords",
        "x": {"__value": 1, "__type": "int"},
        "y": {"__value": 2, "__type": "int"},
        "random": {"__value": coord.random, "__type": "int"},
    }


# *==================EXPORTER AND IMPORTER=====================
@pytest.fixture
def graph(custom_value):

    graph = Graph()

    a, b, c = graph.add_node(
        Node("A", color="#FF00FF"),
        Node("B", coords=custom_value(6, 7)),
        custom_value(1, 2),
    )

    a._id = "N0"
    b._id = "N1"
    c._id = "N3"

    a.add_relation((b, 5), (c, 10))
    return graph


def test_export_import_csv(graph):
    Exporter(graph).to_csv("file.csv")

    import_ = Importer()
    graph2, nodes = import_.nodes_from_csv("file_nodes.csv")

    import_.relations_from_csv("file_relations.csv", nodes)

    search = SearchAlgorithm(BFSFrontier())
    assert search.search(graph2, nodes["N0"], nodes["N3"]) == NodeSolution(
        nodes["N3"]
    ).add_steps(Relation(nodes["N0"], nodes["N3"], 10))

    assert nodes["N0"].color == "#FF00FF"

    assert nodes["N1"].coords.x == 6
    assert nodes["N1"].coords.y == 7

    assert nodes["N3"].value.x == 1
    assert nodes["N3"].value.y == 2

    os.remove("file_nodes.csv")
    os.remove("file_relations.csv")


def test_export_import_json(graph):
    Exporter(graph).to_json("file.json")

    import_ = Importer()
    graph2, nodes = import_.nodes_from_json("file_nodes.json")

    import_.relations_from_json("file_relations.json", nodes)

    search = SearchAlgorithm(BFSFrontier())
    assert search.search(graph2, nodes["N0"], nodes["N3"]) == NodeSolution(
        nodes["N3"]
    ).add_steps(Relation(nodes["N0"], nodes["N3"], 10))

    assert nodes["N0"].color == "#FF00FF"

    assert nodes["N1"].coords.x == 6
    assert nodes["N1"].coords.y == 7

    assert nodes["N3"].value.x == 1
    assert nodes["N3"].value.y == 2

    os.remove("file_nodes.json")
    os.remove("file_relations.json")