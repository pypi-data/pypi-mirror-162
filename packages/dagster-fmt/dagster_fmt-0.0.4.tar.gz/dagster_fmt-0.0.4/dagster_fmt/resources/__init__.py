import ast
from typing import List, Tuple

from dagster_fmt.shared.create_decorator import create_config, get_decorator_node
from dagster_fmt.shared.insert import InsertText
from dagster_fmt.shared.read_context import get_config_field_names


def add_resource_decorator(node: ast.FunctionDef, config, first_node):
    output = []

    decorator_node = get_decorator_node("resource", node)

    (decorator_config, imports), include = create_config(
        get_config_field_names("resource_config", node),
        config.resources,
    )
    if include:
        output.append(InsertText.after_node(decorator_config, decorator_node))
        output.append(InsertText.before_node(imports, first_node))

    return [
        InsertText("(", decorator_node.lineno - 1, decorator_node.end_col_offset),
        *output,
        InsertText(")", decorator_node.lineno - 1, decorator_node.end_col_offset),
    ]
