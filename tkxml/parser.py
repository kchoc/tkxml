
from typing import Literal
import re

class Node:
    def __init__(self):
        self.name: str = ""
        self.attributes: dict[str, str] = {}
        self.children: list = []
        self.layout_manager: Literal["pack", "grid", "place"] = "pack"

    def __repr__(self):
        return f"Node(name={self.name}, attributes={self.attributes}, children={self.children}, layout_manager={self.layout_manager})"

def get_attribute_value(data: str) -> tuple[str, str]:
    data = data.lstrip()
    match data[0]:
        case "'" | '"':
            match = re.match(r'(["\'])(.*?)(?<!\\)\1', data)
            if not match:
                raise ValueError("Mismatched quotes in attribute value")
            end_quote_index = match.end()
            return data[1:end_quote_index - 1], data[end_quote_index:]

        case "[":
            data = data[1:]
            value = []
            while data[0] != "]":
                element, data = get_attribute_value(data)
                value.append(element)

        case _:
            match = re.match(r'[^/}\]> ]+', data)
            end_space_index = match.end()
            value = data[:end_space_index]
            try:
                return float(value), data[end_space_index:]
            except ValueError:
                return value, data[end_space_index:]

def check_comment(data: str) -> str:
    if data[:2] in ("//", "/*"):
        return check_comment(data[data.index("\n") + 1:].lstrip())
    return data

def parse(data: str) -> tuple[Node, str]:
    node = Node()
    data = check_comment(data.lstrip())
    open_tag = data[0]

    # Select layout manager
    layout_manager_map = {
        "<": ["pack",  ">"],
        "{": ["grid",  "}"],
        "[": ["place", "]"]
    }
    node.layout_manager, close_tag = layout_manager_map.get(open_tag)
    if not node.layout_manager:
        raise ValueError("Invalid TKXML format")
    
    # Return if closing tag
    data = data[1:]
    if data[0] == "/":
        return None, data[data.index(close_tag) + 1:]
    
    # Parse node name
    match = re.match(r'[^/}\]> ]+', data)
    node.name, data = data[:match.end()], data[match.end():]
    
    # Parse attributes
    while data[0] not in "/" + close_tag:
        # Get attribute name
        attribute_name, _, data = data.partition("=")
        data = data.lstrip()

        # Get attribute value
        attribute_value, data = get_attribute_value(data)
        node.attributes[attribute_name.strip()] = attribute_value
        data = data.lstrip()

    # Return if self-closing tag
    if data[0] == "/":
        return node, data[2:]
    
    # Parse children
    data = data[1:]
    while True:
        child, data = parse(data)
        if child is None:
            return node, data
        node.children.append(child)
        
if __name__ == "__main__":
    data = "<frame layout=grid><button text='Hello, World!' row=0 column=0 /></frame>"
    root, _ = parse(data)
    print(root.children)