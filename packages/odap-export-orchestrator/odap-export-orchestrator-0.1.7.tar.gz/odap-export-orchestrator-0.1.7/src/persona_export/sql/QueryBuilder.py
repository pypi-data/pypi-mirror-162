from pydantic import BaseModel
from typing import List, Union, Optional, Any

class Attribute(BaseModel):
    '''Attribute schema'''
    op: str
    id: str
    value: Any

class Query(BaseModel):
    '''Basic query schema'''
    attributes: List[Attribute]
    op: str

class Cell:
    def __init__(self, cell: dict):
        self.query = []
        for attribute in cell.attributes:
            self.query.append(
                f'({eval("self."+attribute.op.lower()+"(attribute)")})'
            )
            self.query.append(
                attribute.condition
                if hasattr(attribute, "condition")
                else "and"
            )

    def between(self, item):
        return f"({item.id} >= {item.value[0]}) and ({item.id} <= {item.value[1]})"

    def greater_than(self, item):
        return f"{item.id} >= {item.value}"

    def less_than(self, item):
        return f"{item.id} <= {item.value}"

    def equals(self, item):
        if isinstance(item.value, list):
            query = []
            for value in item.value:
                query.append(f"({item.id} == '{value}')")
            return " or ".join(query)
        elif item.value in [True, False]:
            return f"{item.id} == {'1' if item.value else '0'}"
        else:
            return f"{item.id} == {item.value}"

    def not_equals(self, item):
        if isinstance(item.value, list):
            query = []
            for value in item.value:
                query.append(f"({item.id} != '{value}')")
            return " or ".join(query)
        elif item.value in [True, False]:
            return f"{item.id} == {'0' if item.value else '1'}"
        else:
            return f"{item.id} != {item.value}"


def query_build(query):
    final_query = []
    for item in query:
        item = Query(**item)
        final_query.append(f"({' '.join(Cell(item).query[:-1]).strip()})")
        final_query.append(f"{item.op}")
    return " ".join(final_query[:-1]).strip()
