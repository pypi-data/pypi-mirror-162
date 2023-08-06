# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dagster_fmt',
 'dagster_fmt.ops',
 'dagster_fmt.resources',
 'dagster_fmt.shared',
 'dagster_fmt.tool']

package_data = \
{'': ['*']}

install_requires = \
['black>=22.6.0,<23.0.0', 'isort>=5.10.1,<6.0.0', 'toml>=0.10.2,<0.11.0']

entry_points = \
{'console_scripts': ['dagster_fmt = dagster_fmt.__main__:cli']}

setup_kwargs = {
    'name': 'dagster-fmt',
    'version': '0.0.4',
    'description': 'Dagster code gen tool',
    'long_description': '# `dagster_fmt`\n\nCreate an execution function and have `dagster_fmt` fill out the decorator arguments.\n\n> Disclaimer: This project is not affiliated with Dagster.\n\n## Example\n\nFor example, let\'s say we have the following `op`:\n```python\nfrom dagster import Output, op\n\n@op\ndef some_op1(context, a, b):\n    c = context.op_config["c_field"]\n    context.resources.some_resource.some_method(a, b, c)\n\n    return Output(1, output_name="a")\n```\n\nThere are a couple of things we can infer from the body of the execution function:\n* There must be a configuration field called `c_field` because of it\'s access on line 3\n* There must be a resource called `some_resource` because of it\'s access on line 4\n* There is a single output named `a` from the return statement\n* The `context` argument can have a type annotation of `OpExecutionContext`\n\nWe also think it would be helpful to have descriptions on the op, it\'s inputs, config and outputs.\nIn the op input, a `Nothing` dependency can also be specified for more use cases later down the road.\n\n\nAfter running `dagster_fmt` on the file (formatting, and import sorting), the above op is converted to the following:\n\n```python\nfrom typing import Any\n\nimport dagster\nfrom dagster import Field, In, Nothing, OpExecutionContext, Out, Output, op\n\n@op(\n    ins={\n        "a": In(dagster_type=Any, description=""),\n        "b": In(dagster_type=Any, description=""),\n        "run_after": In(\n            dagster_type=Nothing,\n            description="Placeholder dependency for orchestration with other ops.",\n        ),\n    },\n    config_schema={\n        "c_field": Field(\n            config=dagster.Any, description="", is_required=True, default_value=""\n        )\n    },\n    out={"a": Out(description="", is_required=True)},\n    required_resource_keys={"some_resource"},\n)\ndef some_op1(context: OpExecutionContext, a, b):\n    """Op description"""\n\n    c = context.op_config["c_field"]\n    context.resources.some_resource.some_method(a, b, c)\n\n    return Output(1, output_name="a")\n```\n\nThe point of this tool is to save on a lot of typing and to create a template to fill in with descriptions and type annotations. More arguments are created than needed, but you can simply delete them.\n\nThe command only modies blank ops (without arguments) as to not modify existing code.\n\n## Configuration Options\n\nConfiguration can be specified in the `pyproject.toml`. The following options are listed below.\n\nIn the `tool.dagster_fmt` section, there are options which apply to both ops and resources. The values in the individual ops and resources sections override these values.\n\n### tool.dagster_fmt\n* `add_docstrings: boolean [default=True]` Whether to add docstrings to the execution function.\n* `add_descriptions: boolean [default=True]` Whether to add a `description=""` to applicable dagster classes.\n* `add_is_required: boolean [default=True]` Whether to add a `is_required=True` to applicable dagster classes.\n* `dir: string [default="*"]` Subdirectory to format files in. For example if `dir = "ops"` then running `dagster_fmt .` only formats files matching the path `**/ops/*.py`. By default, ignore sub directories.\n\n### tool.dagster_fmt.ops\n* `add_docstrings: boolean [default=tool.dagster_fmt.add_docstrings]` Whether to add docstrings to the execution function.\n* `add_descriptions: boolean [default=tool.dagster_fmt.add_descriptions]` Whether to add a `description=""` to Ins, Fields, Outs and DynamicOuts.\n* `add_no_data_dep_in: boolean [default=True]` Whether to add a `dagster_type=Nothing` In to the op.\n* `no_data_dep_name: string [default="run_after"]` Name of the no data dependency input.\n* `add_is_required: boolean [default=tool.dagster_fmt.add_is_required]` Whether to add a `is_required=True` to Fields, Outs and DynamicOuts.\n\n### tool.dagster_fmt.resources\n* `add_docstrings: boolean [default=tool.dagster_fmt.add_docstrings]` Whether to add docstrings to the execution function.\n* `add_descriptions: boolean [default=tool.dagster_fmt.add_descriptions]` Whether to add a `description=""` Fields.\n* `add_is_required: boolean [default=tool.dagster_fmt.add_is_required]` Whether to add a `is_required=True` to Fields.\n',
    'author': 'arudolph',
    'author_email': 'alex3rudolph@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.github.com/alrudolph/dagster_fmt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
