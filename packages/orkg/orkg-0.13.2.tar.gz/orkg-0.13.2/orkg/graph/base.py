class ORKGNode:
    def __init__(
            self,
            id: str,
            label: str,
            class_: str,
            classes: list = None,
            description: str = None,
            datatype: str = None
    ):
        self.id = id
        self.label = label
        self.class_ = class_
        self.classes = classes
        self.description = description
        self.datatype = datatype

    def __repr__(self):
        return 'ORKGNode({})'.format(self.id)


class ORKGEdge:
    def __init__(
            self,
            id: str,
            label: str,
            class_: str
    ):
        self.id = id
        self.label = label
        self.class_ = class_

    def __repr__(self):
        return 'ORKGEdge({})'.format(self.id)
