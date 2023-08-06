import ast
from typing import List, Tuple

from dagster_fmt.tool.schema import Config


def is_node(decorator_name: str, node) -> bool:
    """Whether this ast node is for an Op or Resource function

    Params
    ------
    decorator_name: str
        'op' or 'resource'
    node
        Any ast node

    Returns
    -------
    is_node: bool
    """
    return isinstance(node, ast.FunctionDef) and any(
        [hasattr(n, "id") and decorator_name == n.id for n in node.decorator_list]
    )


def create_config(
    config_names: List[str], config: Config
) -> Tuple[Tuple[str, str], bool]:
    """Create config schema for the decorator

    Params
    ------
    config_names: List[str]
        Field names to add config for
    config: Config
        Op or resource configuration rules

    Returns
    -------
    (config_schema, imports), to_include
        The config schema text, import text and whether to include this text
    """
    if len(config_names) == 0:
        return "", False

    desc: str = 'description="", ' if config.add_descriptions else ""
    is_req: str = "is_required=True, " if config.add_is_required else ""

    config_schema_inner = ",".join(
        [
            f'"{c}": Field(config=dagster.Any, {desc}{is_req}default_value=None)'
            for c in config_names
        ]
    )

    return (
        (
            "config_schema={" + config_schema_inner + "},",
            "import dagster\nfrom dagster import Field\n",
        ),
        True,
    )


def get_decorator_node(node_name: str, function_node: ast.FunctionDef):
    """Get the node for the function's decorator

    Params
    ------
    node_name: str
        The @`node_name` decorator name
    function_node: ast.FunctionDef
        Function node to get decorators of

    Returns
    -------
    decorator_node
        Decorator node
    """
    for decorator in function_node.decorator_list:
        if decorator.id == node_name:
            return decorator
