"""Python-to-English translation tools."""

import ast


def translate_assignment(statement: ast.Assign) -> str:
    """Translate a Python assignment into plain English."""
    target = ast.unparse(statement.targets[0])
    value = ast.unparse(statement.value)
    return f"Set {target} equal to {value}."


def translate_python(python_code: str) -> str:
    """Translate Python source code into plain English."""
    tree = ast.parse(python_code)
    translations: list[str] = []

    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            translation = translate_assignment(statement)
            translations.append(translation)

    return "\n".join(translations)
