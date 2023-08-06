import ast
from typing import List, Tuple

from dagster_fmt.shared.create_decorator import create_config, get_decorator_node
from dagster_fmt.shared.insert import InsertText
from dagster_fmt.shared.read_context import get_config_field_names


def get_resource_names(function_node: ast.FunctionDef) -> List[str]:
    """Get the names of the resources being used.

    Params
    ------
    function_node: ast.FunctionDef
        Node to parse through

    Returns
    -------
    resource_names: List[str]
        Names of the resource being used by `context.resources.[resource_name]`
    """
    output = []

    for possible_resource_access in ast.walk(function_node):

        if (
            isinstance(possible_resource_access, ast.Attribute)
            and hasattr(possible_resource_access, "value")
            and hasattr(possible_resource_access.value, "attr")
            and possible_resource_access.value.attr == "resources"
            and possible_resource_access.value.value.id == "context"
        ):
            output.append(possible_resource_access.attr)

    return output


def create_required_resource_keys(resources: List[str]) -> str:
    if len(resources) == 0:
        return ""

    return 'required_resource_keys={"' + '","'.join(resources) + '"},'


def get_op_ins(node: ast.FunctionDef) -> List[str]:
    output = []

    for arg in node.args.args:

        if arg.arg != "context":

            anno = None

            if arg.annotation is not None:
                anno = arg.annotation.id

            output.append({"name": arg.arg, "annotation": anno})

    return output


def create_op_ins(ins: List[str], config):
    if len(ins) == 0:
        return "", False

    desc = 'description=""' if config.ops.add_descriptions else ""
    imports = []

    def create_n(c):
        _type = ""

        if c["annotation"] is None:
            _type = "dagster_type=Any"
            imports.append("from typing import Any")

        if _type != "" and desc != "":
            _type += ", "

        imports.append("from dagster import In")

        return f"In({_type}{desc})"

    if config.ops.add_no_data_dep_in:
        no_data_dep = f',"{config.ops.no_data_dep_name}": In(dagster_type=Nothing, description="Placeholder dependency for orchestration with other ops.")'
        imports.append("from dagster import Nothing")
    else:
        no_data_dep = ""

    return (
        (
            "ins={"
            + ",".join(['"' + c["name"] + f'": {create_n(c)}' for c in ins])
            + no_data_dep
            + "},",
            "\n".join(imports) + "\n",
        ),
        True,
    )


def get_op_out(node: ast.FunctionDef):
    output_type = {"Output": "Out", "DynamicOutput": "DynamicOut"}
    output = []

    for return_node in ast.walk(node):
        ot = "Output"
        name = "op_output"
        anno = None

        if not isinstance(return_node, ast.Yield) and not isinstance(
            return_node, ast.Return
        ):
            continue

        if isinstance(return_node.value, ast.Call):
            ot = return_node.value.func.id

            if ot in output_type.keys():
                name = [
                    k for k in return_node.value.keywords if k.arg == "output_name"
                ][0].value.value

                # figure out from class
                anno = None
            else:
                # name = f"op_output_{len(output)}"
                # ot = "Output"
                #
                # If you return a value directly from a function, it doesn't get picked up
                # but we also don't want yielding of assetmaterilizations. We can add more
                # logic for that later
                continue
        elif isinstance(return_node.value, ast.Tuple):
            # if the output is a tuple, for example:
            #
            # ```
            # return 1, 2
            # ```
            #
            # This could either be a single output tuple, or two output ints.
            # Here we assume that it's two outputs because I think it's easier /
            # preferred to delete a line than add another, and one should
            # change the output name anyways
            for val in return_node.value.elts:
                output.append(
                    {
                        "name": f"maybe_out_{len(output)}",
                        "type": output_type[ot],
                        "annotation": type(val.value).__name__,
                    }
                )

            continue
        else:
            anno = type(return_node.value.value).__name__

        output.append({"name": name, "type": output_type[ot], "annotation": anno})

    if len(output) == 1:
        # if you only have one output, then put it as a type annotation on the function ?
        # maybe not?
        output[0]["annotation"] = None

    return output


def create_op_out(out, config):
    if len(out) == 0:
        return "", False

    # having the `is_required=True` explicity typed makes it easier
    # to remember what the kwarg's name is
    desc = 'description=""' if config.ops.add_descriptions else ""
    is_req = "is_required=True" if config.ops.add_is_required else ""
    imports = []

    def get_anno(c):
        if c["annotation"] is None:
            anno = "dagster_type=Any"
            imports.append("from typing import Any")
        else:
            anno = f"dagster_type={c['annotation']}"

        imports.append(f"from dagster import {c['type']}")

        if c["annotation"] == "Any":
            imports.append(f"from typing import Any")

        return (
            anno
            + (f", {desc}" if desc != "" else "")
            + (f", {is_req}" if is_req != "" else "")
        )

    return (
        (
            "out={"
            + ",".join(
                ['"' + c["name"] + f'" : {c["type"]}({get_anno(c)})' for c in out]
            )
            + "},",
            "\n".join(imports) + "\n",
        ),
        True,
    )


def add_op_decorator(node: ast.FunctionDef, config, first_node):
    output = []

    #
    # get existing config
    #

    decorator_node = get_decorator_node("op", node)

    i_str, include = create_op_ins(get_op_ins(node), config)
    if include:
        output.append(InsertText.after_node(i_str[0], decorator_node))
        output.append(InsertText.before_node(i_str[1], first_node))

    c_str, include = create_config(
        get_config_field_names("op_config", node), config.ops
    )
    if include:
        output.append(InsertText.after_node(c_str[0], decorator_node))
        output.append(InsertText.before_node(c_str[1], first_node))

    o_str, include = create_op_out(get_op_out(node), config)
    if include:
        output.append(InsertText.after_node(o_str[0], decorator_node))
        output.append(InsertText.before_node(o_str[1], first_node))

    r_str = create_required_resource_keys(get_resource_names(node))
    if r_str != "":
        output.append(InsertText.after_node(r_str, decorator_node))

    return [
        InsertText("(", decorator_node.lineno - 1, decorator_node.end_col_offset),
        *output,
        InsertText(")", decorator_node.lineno - 1, decorator_node.end_col_offset),
    ]
