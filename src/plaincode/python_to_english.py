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
    return f"Print {argument}."


def translate_function_definition(statement: ast.FunctionDef) -> str:
    parameters: list[str] = []

    for argument in statement.args.args:
        parameters.append(argument.arg)

        parameter_text = ", ".join(parameters)

        header = (
            f"Define a function named {statement.name} "
            f"that accepts the parameter {parameter_text}."
        )

        translations: list[str] = [header]

        for nested_statement in statement.body:
            nested_translation = translate_statement(nested_statement)
            translations.append(indent_translation(nested_translation))

        return "\n".join(translations)


def translate_statement(statement: ast.stmt) -> str:
    """Translate one Python statement into plain English."""
    if isinstance(statement, ast.Assign):
        return translate_assignment(statement)

    if isinstance(statement, ast.FunctionDef):
        return translate_function_definition(statement)

    if isinstance(statement, ast.If):
        return translate_if_statement(statement)

    if isinstance(statement, ast.Expr):
        call = statement.value

        if isinstance(call, ast.Call):
            function = call.func

            if isinstance(function, ast.Name) and function.id == "print":
                return translate_print_call(call)

    return "Unsupported statement."


def indent_translation(translation: str) -> str:
    """Indent every line of a translation by four spaces."""
    indented_lines = (
        f"    {line}" for line in translation.splitlines()
    )
    return "\n".join(indented_lines)


def translate_comparison(comparison: ast.Compare) -> str:
    left = ast.unparse(comparison.left)
    operator = comparison.ops[0]
    right = ast.unparse(comparison.comparators[0])

    if isinstance(operator, ast.Gt):
        return f"{left} is greater than {right}"
    if isinstance(operator, ast.Lt):
        return f"{left} is less than {right}"
    if isinstance(operator, ast.GtE):
        return f"{left} is greater than or equal to {right}"
    if isinstance(operator, ast.LtE):
        return f"{left} is less than or equal to {right}"
    if isinstance(operator, ast.Eq):
        return f"{left} is equal to {right}"
    if isinstance(operator, ast.NotEq):
        return f"{left} is not equal to {right}"
    
    return "Unsupported comparison"


def translate_if_statement(statement: ast.If) -> str:
    """Translate a Python if statement into plain English."""
    if not isinstance(statement.test, ast.Compare):
        return "Unsupported if condition"

    condition = translate_comparison(statement.test)
    translations: list[str] = [f"If {condition}:"]

    for nested_statement in statement.body:
        nested_translation = translate_statement(nested_statement)
        translations.append(indent_translation(nested_translation))

    return "\n".join(translations)



def translate_python(python_code: str) -> str:
    """Translate Python source code into plain English."""
    tree = ast.parse(python_code)
    translations: list[str] = []

    for statement in tree.body:
        translation = translate_statement(statement)
        translations.append(translation)

    return "\n".join(translations)
