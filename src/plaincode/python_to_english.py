"""Python-to-English translation tools."""

import ast


def translate_assignment(statement: ast.Assign) -> str:
    """Translate a Python assignment into plain English."""
    target = ast.unparse(statement.targets[0])
    value = ast.unparse(statement.value)
    return f"Set {target} equal to {value}."


def translate_print_call(call: ast.Call) -> str:
    """Translate a Python print call into plain English."""
    argument = ast.unparse(call.args[0])
    return f"Print {argument}"


def translate_python(python_code: str) -> str:
    """Translate Python source code into plain English."""
    tree = ast.parse(python_code)
    translations: list[str] = []

    for statement in tree.body:
        if isinstance(statement, ast.Assign):
            translation = translate_assignment(statement)
            translations.append(translation)
        elif isinstance(statement, ast.Expr):
            call = statement.value

            if isinstance(call, ast.Call):
                function = call.func

                if isinstance(function, ast.Name) and function.id == "print":
                    translation = translate_print_call(call)
                    translations.append(translation)

    return "\n".join(translations)
