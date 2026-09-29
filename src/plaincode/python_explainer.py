"""Python explanation tools."""

import ast

from plaincode.python_to_english import (
    translate_expression,
    translate_statement,
)


def describe_value(expression: ast.expr) -> str:
    """Describe a Python value in readable English."""
    if isinstance(expression, ast.Constant):
        if expression.value == "\n":
            return "a newline character"

        if expression.value == "\t":
            return "a tab character"

    return translate_expression(expression)


def explain_expression(
    expression: ast.expr,
) -> tuple[list[str], str]:
    """Explain an expression in execution order."""
    if isinstance(expression, ast.Call):
        if isinstance(expression.func, ast.Attribute):
            if (
                expression.func.attr == "split"
                and len(expression.args) == 1
            ):
                previous_steps, value = explain_expression(
                    expression.func.value
                )

                separator = describe_value(
                    expression.args[0]
                )

                steps = previous_steps + [
                    f"Split {value} wherever {separator} appears."
                ]

                if (
                    isinstance(expression.args[0], ast.Constant)
                    and expression.args[0].value == "\n"
                ):
                    result = "the resulting lines"
                else:
                    result = "the resulting pieces"

                return steps, result

            if (
                expression.func.attr == "join"
                and len(expression.args) == 1
            ):
                previous_steps, value = explain_expression(
                    expression.args[0]
                )

                separator = describe_value(
                    expression.func.value
                )

                steps = previous_steps + [
                    (
                        f"Join {value} using {separator} "
                        "between each item."
                    )
                ]

                return steps, "the resulting string"

        if isinstance(expression.func, ast.Name):
            if (
                expression.func.id == "map"
                and len(expression.args) == 2
            ):
                function_name = ast.unparse(
                    expression.args[0]
                )

                previous_steps, value = explain_expression(
                    expression.args[1]
                )

                steps = previous_steps + [
                    (
                        f"Apply {function_name} to each item "
                        f"in {value}."
                    )
                ]

                return steps, "the resulting sequence"

    return [], translate_expression(expression)


def explain_return(statement: ast.Return) -> list[str]:
    """Explain a return statement."""
    if statement.value is None:
        return ["Return without a value."]

    steps, result = explain_expression(statement.value)

    if steps:
        steps.append(f"Return {result}.")
        return steps

    return [translate_statement(statement)]


def explain_function(
    statement: ast.FunctionDef,
) -> list[str]:
    """Explain a function and its body."""
    parameters = [
        argument.arg
        for argument in statement.args.args
    ]

    if not parameters:
        parameter_description = "no parameters"
    elif len(parameters) == 1:
        parameter_description = (
            f"the parameter {parameters[0]}"
        )
    else:
        leading_parameters = ", ".join(
            parameters[:-1]
        )
        parameter_description = (
            f"the parameters {leading_parameters} "
            f"and {parameters[-1]}"
        )

    lines = [
        (
            f"Function {statement.name} accepts "
            f"{parameter_description}:"
        )
    ]

    for nested_statement in statement.body:
        if isinstance(nested_statement, ast.Return):
            explanation = explain_return(
                nested_statement
            )
        else:
            explanation = [
                translate_statement(nested_statement)
            ]

        for line in explanation:
            lines.append(f"    {line}")

    return lines


def explain_python(python_code: str) -> str:
    """Explain Python source code in execution-oriented English."""
    tree = ast.parse(python_code)

    explanations: list[str] = []

    for statement in tree.body:
        if isinstance(statement, ast.FunctionDef):
            explanation = explain_function(statement)
            explanations.extend(explanation)
        elif isinstance(statement, ast.Return):
            explanations.extend(
                explain_return(statement)
            )
        else:
            explanations.append(
                translate_statement(statement)
            )

    return "\n".join(explanations)