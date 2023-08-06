# `dagster_fmt`

Create an execution function and have `dagster_fmt` fill out the decorator arguments.

> Disclaimer: This project is not affiliated with Dagster.

## Example

For example, let's say we have the following `op`:
```python
from dagster import Output, op

@op
def some_op1(context, a, b):
    c = context.op_config["c_field"]
    context.resources.some_resource.some_method(a, b, c)

    return Output(1, output_name="a")
```

There are a couple of things we can infer from the body of the execution function:
* There must be a configuration field called `c_field` because of it's access on line 3
* There must be a resource called `some_resource` because of it's access on line 4
* There is a single output named `a` from the return statement
* The `context` argument can have a type annotation of `OpExecutionContext`

We also think it would be helpful to have descriptions on the op, it's inputs, config and outputs.
In the op input, a `Nothing` dependency can also be specified for more use cases later down the road.


After running `dagster_fmt` on the file (formatting, and import sorting), the above op is converted to the following:

```python
from typing import Any

import dagster
from dagster import Field, In, Nothing, OpExecutionContext, Out, Output, op

@op(
    ins={
        "a": In(dagster_type=Any, description=""),
        "b": In(dagster_type=Any, description=""),
        "run_after": In(
            dagster_type=Nothing,
            description="Placeholder dependency for orchestration with other ops.",
        ),
    },
    config_schema={
        "c_field": Field(
            config=dagster.Any, description="", is_required=True, default_value=""
        )
    },
    out={"a": Out(description="", is_required=True)},
    required_resource_keys={"some_resource"},
)
def some_op1(context: OpExecutionContext, a, b):
    """Op description"""

    c = context.op_config["c_field"]
    context.resources.some_resource.some_method(a, b, c)

    return Output(1, output_name="a")
```

The point of this tool is to save on a lot of typing and to create a template to fill in with descriptions and type annotations. More arguments are created than needed, but you can simply delete them.

The command only modies blank ops (without arguments) as to not modify existing code.

## Configuration Options

Configuration can be specified in the `pyproject.toml`. The following options are listed below.

In the `tool.dagster_fmt` section, there are options which apply to both ops and resources. The values in the individual ops and resources sections override these values.

### tool.dagster_fmt
* `add_docstrings: boolean [default=True]` Whether to add docstrings to the execution function.
* `add_descriptions: boolean [default=True]` Whether to add a `description=""` to applicable dagster classes.
* `add_is_required: boolean [default=True]` Whether to add a `is_required=True` to applicable dagster classes.
* `dir: string [default="*"]` Subdirectory to format files in. For example if `dir = "ops"` then running `dagster_fmt .` only formats files matching the path `**/ops/*.py`. By default, ignore sub directories.

### tool.dagster_fmt.ops
* `add_docstrings: boolean [default=tool.dagster_fmt.add_docstrings]` Whether to add docstrings to the execution function.
* `add_descriptions: boolean [default=tool.dagster_fmt.add_descriptions]` Whether to add a `description=""` to Ins, Fields, Outs and DynamicOuts.
* `add_no_data_dep_in: boolean [default=True]` Whether to add a `dagster_type=Nothing` In to the op.
* `no_data_dep_name: string [default="run_after"]` Name of the no data dependency input.
* `add_is_required: boolean [default=tool.dagster_fmt.add_is_required]` Whether to add a `is_required=True` to Fields, Outs and DynamicOuts.

### tool.dagster_fmt.resources
* `add_docstrings: boolean [default=tool.dagster_fmt.add_docstrings]` Whether to add docstrings to the execution function.
* `add_descriptions: boolean [default=tool.dagster_fmt.add_descriptions]` Whether to add a `description=""` Fields.
* `add_is_required: boolean [default=tool.dagster_fmt.add_is_required]` Whether to add a `is_required=True` to Fields.
