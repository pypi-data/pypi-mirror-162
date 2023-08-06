import ast

from dagster_fmt.shared.insert import InsertText


def add_docstring(docstring_text: str, node: ast.FunctionDef):
    """Add a docstring to the function body

    Params
    ------
    docstring_text: str
        Text to insert in the docstring
    node: ast.FunctionDef
        Function node

    Returns
    -------
    insert: InsertText | None
        Where and what to insert
    """
    n_body = node.body[0]

    if (
        isinstance(n_body, ast.Expr)
        and isinstance(n_body.value, ast.Constant)
        and isinstance(n_body.value.value, str)
    ):
        if n_body.value.value.endswith("\n"):
            return

        return InsertText.after_node("\n", n_body)

    return InsertText.before_node(
        '"""' + docstring_text + '"""\n', n_body, newline=True
    )
