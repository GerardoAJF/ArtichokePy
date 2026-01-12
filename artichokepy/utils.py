import typing as t

from artichokepy.graph import Node, Relation

class NodePath:
    def __init__(self, node: Node) -> None:
        self.node = node
        self.nodes: t.Set[Node] = {node, }
        self.path: t.List[Relation] = []

    def __repr__(self) -> str:
        return f"{self.node} :: {' & '.join(str(relation) for relation in self.path)}"

    def add_steps(self, *relations: Relation) -> t.Self:
        """ TODO: agregar validaciones para que los pasos sean "verdaderos pasos"
            no cualquier relación ni en cualquier orden
        """
        
        for relation in relations:
            self.path.append(relation)
            self.nodes.add(relation.end)
        return self

    def get_previous_node(self, step=1) -> Node:
        if len(self.path) < step:
            step = 0

        return self.path[-step].init

    def __eq__(self, value: object) -> bool:
        if isinstance(value, NodePath):
            return self.node == value.node and self.path == value.path
        return False

    def __hash__(self) -> int:
        return hash((self.node, *self.path))
