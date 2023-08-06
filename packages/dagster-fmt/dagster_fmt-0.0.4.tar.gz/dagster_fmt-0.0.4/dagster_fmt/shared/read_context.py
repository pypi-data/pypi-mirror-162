import ast
from typing import List


def get_config_field_names(
    config_name: str,
    function_node: ast.FunctionDef,
) -> List[str]:
    """Get the keys of the context's config dictionary.

    Params
    ------
    config_name: str
        Name of the config attribute. E.g. 'op_config' or 'resource_config'
    function_node: ast.FunctionDef
        Node to parse through

    Returns
    -------
    config_field_names: List[str]
        Names of all of the accessed config in the function body
    """
    output = []

    for possible_dict_access in ast.walk(function_node):

        if (
            isinstance(possible_dict_access, ast.Subscript)
            and possible_dict_access.value.value.id == "context"
            and possible_dict_access.value.attr == config_name
        ):
            output.append(possible_dict_access.slice.value.value)

    return output
