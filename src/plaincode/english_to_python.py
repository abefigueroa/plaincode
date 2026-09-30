"""English-to-Python translation tools."""

import ast
import re


class UnsupportedEnglishError(ValueError):
    """Raised when PlainCode cannot translate an English statement."""


def translate_expression(expression: str) -> str:
    """Translate a PlainCode English expression into Python."""
    expression = expression.strip()
    lowered_expression = expression.lower()

    lambda_prefix = "a lambda that accepts "

    if lowered_expression.startswith(lambda_prefix):
        content = expression[len(lambda_prefix):]
        lowered_content = content.lower()

        if " and returns " in lowered_content:
            separator = " and returns "
            separator_index = lowered_content.index(separator)

            parameter = content[:separator_index]
            body = content[
                separator_index + len(separator):
            ]

            try:
                translated_body = translate_condition(body)
            except UnsupportedEnglishError:
                translated_body = translate_expression(body)

            return f"lambda {parameter}: {translated_body}"
        
    if lowered_expression.startswith("filter "):
        content = expression[len("filter "):]
        lowered_content = content.lower()

        if " using " in lowered_content:
            separator = " using "
            separator_index = lowered_content.index(separator)

            iterable = content[:separator_index]
            function = content[
                separator_index + len(separator):
            ]

            translated_iterable = translate_expression(iterable)
            translated_function = translate_expression(function)

            return (
                f"filter({translated_function}, "
                f"{translated_iterable})"
            )

    if " split by " in lowered_expression:
        separator = " split by "
        separator_index = lowered_expression.index(separator)

        value = expression[:separator_index]
        delimiter = expression[
            separator_index + len(separator):
        ]

        translated_value = translate_expression(value)
        translated_delimiter = translate_expression(delimiter)

        return (
            f"{translated_value}.split("
            f"{translated_delimiter})"
        )

    if lowered_expression.startswith("the length of "):
        value = expression[len("the length of "):]
        return f"len({translate_expression(value)})"

    if lowered_expression.startswith("a sorted copy of "):
        value = expression[len("a sorted copy of "):]
        return f"sorted({translate_expression(value)})"

    operators = {
        " plus ": "+",
        " minus ": "-",
        " multiplied by ": "*",
        " divided by ": "/",
        " floor divided by ": "//",
        " modulo ": "%",
        " raised to the power of ": "**",
    }

    for english_operator, python_operator in operators.items():
        if english_operator in expression:
            left, right = expression.split(english_operator, 1)

            translated_left = translate_expression(left)
            translated_right = translate_expression(right)

            return (
                f"{translated_left} "
                f"{python_operator} "
                f"{translated_right}"
            )

    try:
        ast.parse(expression, mode="eval")
    except SyntaxError as error:
        raise UnsupportedEnglishError(
            f"Unsupported expression: {expression}"
        ) from error

    return expression


def translate_function_definition(statement: str) -> str:
    """Translate a PlainCode function definition into Python."""
    statement = statement.strip()

    prefix = "Define a function named "
    lowered_statement = statement.lower()

    if not lowered_statement.startswith(prefix.lower()):
        raise UnsupportedEnglishError(
            f"Unsupported function definition: {statement}"
        )

    content = statement[len(prefix):]

    if " that accepts " not in content:
        raise UnsupportedEnglishError(
            f"Unsupported function definition: {statement}"
        )

    function_name, parameter_text = content.split(
        " that accepts ",
        1,
    )

    parameter_text = parameter_text.rstrip(".")

    if parameter_text.lower() == "no parameters":
        parameters = ""

    elif parameter_text.lower().startswith("the parameter "):
        parameters = parameter_text[len("the parameter "):]

    elif parameter_text.lower().startswith("the parameters "):
        parameters = parameter_text[len("the parameters "):]

        if " and " in parameters:
            leading_parameters, last_parameter = parameters.rsplit(
                " and ",
                1,
            )

            parameters = (
                f"{leading_parameters}, {last_parameter}"
            )

    else:
        raise UnsupportedEnglishError(
            f"Unsupported parameter description: {parameter_text}"
        )

    return f"def {function_name}({parameters}):"


def translate_condition(condition: str) -> str:
    """Translate a PlainCode condition into Python."""
    condition = condition.strip()
    lowered_condition = condition.lower()

    if " and " in lowered_condition:
        parts = condition.split(" and ")
        translated_parts = [
            translate_condition(part)
            for part in parts
        ]
        return " and ".join(translated_parts)

    if " or " in lowered_condition:
        parts = condition.split(" or ")
        translated_parts = [
            translate_condition(part)
            for part in parts
        ]
        return " or ".join(translated_parts)

    if lowered_condition.startswith("not "):
        inner_condition = condition[4:]
        translated_condition = translate_condition(
            inner_condition
        )
        return f"not {translated_condition}"

    if " starts with " in lowered_condition:
        separator = " starts with "
        separator_index = lowered_condition.index(separator)

        value = condition[:separator_index]
        prefix = condition[
            separator_index + len(separator):
        ]

        translated_value = translate_expression(value)
        translated_prefix = translate_expression(prefix)

        return (
            f"{translated_value}.startswith("
            f"{translated_prefix})"
        )

    operators = {
        " is greater than or equal to ": ">=",
        " is less than or equal to ": "<=",
        " is not equal to ": "!=",
        " is greater than ": ">",
        " is less than ": "<",
        " is equal to ": "==",
    }

    for english_operator, python_operator in operators.items():
        if english_operator in lowered_condition:
            separator_index = lowered_condition.index(
                english_operator
            )

            left = condition[:separator_index]
            right = condition[
                separator_index + len(english_operator):
            ]

            translated_left = translate_expression(left)
            translated_right = translate_expression(right)

            return (
                f"{translated_left} "
                f"{python_operator} "
                f"{translated_right}"
            )

    raise UnsupportedEnglishError(
        f"Unsupported condition: {condition}"
    )


def translate_if_statement(statement: str) -> str:
    """Translate a PlainCode if statement into Python."""
    statement = statement.strip()

    if not statement.lower().startswith("if "):
        raise UnsupportedEnglishError(
            f"Unsupported if statement: {statement}"
        )

    if not statement.endswith(":"):
        raise UnsupportedEnglishError(
            f"Unsupported if statement: {statement}"
        )

    condition = statement[3:-1]
    translated_condition = translate_condition(condition)

    return f"if {translated_condition}:"

def translate_statement(statement: str) -> str:
    """Translate one PlainCode English statement into Python."""
    statement = statement.strip()
    lowered_statement = statement.lower()

    if lowered_statement.startswith("define a function named "):
        return translate_function_definition(statement)
    
    if lowered_statement.startswith("if "):
        return translate_if_statement(statement)

    if lowered_statement.startswith("elif "):
            if not statement.endswith(":"):
                raise UnsupportedEnglishError(
                    f"Unsupported elif statement: {statement}"
                )
    
            condition = statement[5:-1]
            translated_condition = translate_condition(condition)
    
            return f"elif {translated_condition}:"
    
    if lowered_statement == "else:":
        return "else:"

    if lowered_statement.startswith("set ") and statement.endswith("."):
        content = statement[4:-1]
        lowered_content = content.lower()

        if " equal to " in lowered_content:
            separator_index = lowered_content.index(" equal to ")

            target = content[:separator_index]
            value = content[separator_index + len(" equal to "):]

            translated_value = translate_expression(value)

            return f"{target} = {translated_value}"

    if lowered_statement.startswith("print ") and statement.endswith("."):
        value = statement[6:-1]
        translated_value = translate_expression(value)

        return f"print({translated_value})"

    if lowered_statement == "return.":
        return "return"

    if lowered_statement.startswith("return ") and statement.endswith("."):
        value = statement[7:-1]
        translated_value = translate_expression(value)

        return f"return {translated_value}"

    raise UnsupportedEnglishError(
        f"Unsupported English statement: {statement}"
    )


def translate_english(english_code: str) -> str:
    """Translate PlainCode English into Python source code."""
    translations: list[str] = []

    for line in english_code.splitlines():
        if not line.strip():
            translations.append("")
            continue

        indentation_length = len(line) - len(line.lstrip())
        indentation = line[:indentation_length]

        translated = translate_statement(line.strip())

        translations.append(indentation + translated)

    return "\n".join(translations)


def guess_statement(statement: str) -> str | None:
    """Try to convert casual English into supported PlainCode English."""
    statement = statement.strip()

    set_match = re.fullmatch(
        r"(?:set|make)\s+(\w+)\s+(?:to|equal to)?\s*(.+)",
        statement,
        re.IGNORECASE,
    )

    if set_match:
        target = set_match.group(1)
        value = set_match.group(2).rstrip(".")

        return f"Set {target} equal to {value}."

    print_match = re.fullmatch(
        r"(?:print|show|display)\s+(.+)",
        statement,
        re.IGNORECASE,
    )

    if print_match:
        value = print_match.group(1).rstrip(".")

        return f"Print {value}."

    return_match = re.fullmatch(
        r"(?:return|give back)\s+(.+)",
        statement,
        re.IGNORECASE,
    )

    if return_match:
        value = return_match.group(1).rstrip(".")

        return f"Return {value}."

    return None