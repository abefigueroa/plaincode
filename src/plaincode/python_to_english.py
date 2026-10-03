"""Python-to-English translation tools."""

import ast


def translate_expression(expression: ast.expr) -> str:
    """Translate a Python expression into plain English."""
    if isinstance(expression, ast.BinOp):
        left = translate_expression(expression.left)
        right = translate_expression(expression.right)

        if isinstance(expression.left, ast.BinOp):
            left = f"({left})"

        if isinstance(expression.right, ast.BinOp):
            right = f"({right})"

        if isinstance(expression.op, ast.Add):
            return f"{left} plus {right}"
        if isinstance(expression.op, ast.Sub):
            return f"{left} minus {right}"
        if isinstance(expression.op, ast.Mult):
            return f"{left} multiplied by {right}"
        if isinstance(expression.op, ast.Div):
            return f"{left} divided by {right}"
        if isinstance(expression.op, ast.FloorDiv):
            return f"{left} floor divided by {right}"
        if isinstance(expression.op, ast.Mod):
            return f"{left} modulo {right}"
        if isinstance(expression.op, ast.Pow):
            return f"{left} raised to the power of {right}"

    if isinstance(expression, ast.UnaryOp):
        if isinstance(expression.op, ast.Not):
            operand = translate_expression(expression.operand)
            return f"it is not true that ({operand})"    

    if isinstance(expression, ast.Lambda):
        parameters = [
            argument.arg
            for argument in expression.args.args
        ]

        if len(parameters) == 1:
            parameter_description = parameters[0]
        else:
            parameter_description = ", ".join(parameters)

        if isinstance(
            expression.body,
            (ast.Compare, ast.BoolOp, ast.Call),
        ):
            body = translate_condition(expression.body)
        else:
            body = translate_expression(expression.body)

        return (
            f"a lambda that accepts {parameter_description} "
            f"and returns {body}"
        )
        
    if isinstance(expression, ast.Call):
        if isinstance(expression.func, ast.Name):
            if expression.func.id == "len" and len(expression.args) == 1:
                translated_argument = translate_expression(expression.args[0])
                return f"the length of {translated_argument}"

            if expression.func.id == "sorted":
                if len(expression.args) == 1:
                    translated_argument = translate_expression(expression.args[0])
                    return f"a sorted copy of {translated_argument}"

            if expression.func.id == "map":
                if len(expression.args) == 2:
                    function = translate_expression(expression.args[0])
                    iterable = translate_expression(expression.args[1])
                    return f"map {function} over {iterable}"

            if expression.func.id == "zip":
                if len(expression.args) == 2 and not expression.keywords:
                    first = translate_expression(expression.args[0])
                    second = translate_expression(expression.args[1])
                    return f"items from {first} and {second} paired by position"
            
            if expression.func.id == "filter":
                if len(expression.args) == 2:
                    function = translate_expression(
                        expression.args[0]
                    )
                    iterable = translate_expression(
                        expression.args[1]
                    )

                    return f"filter {iterable} using {function}"

            if expression.func.id == "reduce":
                if len(expression.args) == 2:
                    function = translate_expression(expression.args[0])
                    iterable = translate_expression(expression.args[1])

                    return f"reduce {iterable} using {function}"

            if expression.func.id == "list":
                if len(expression.args) == 1:
                    iterable = translate_expression(
                        expression.args[0]
                    )
                    return f"a list made from {iterable}"

            if expression.func.id == "tuple":
                if len(expression.args) == 1 and not expression.keywords:
                    iterable = translate_expression(expression.args[0])
                    return f"a tuple made from {iterable}"

            if expression.func.id == "set":
                if len(expression.args) == 1 and not expression.keywords:
                    iterable = translate_expression(expression.args[0])
                    return f"a set of unique items from {iterable}"

        if isinstance(expression.func, ast.Attribute):
            if expression.func.attr == "split":
                collection = translate_expression(expression.func.value)

                if len(expression.args) == 1:
                    separator = translate_expression(expression.args[0])
                    return f"{collection} split by {separator}"

            if expression.func.attr == "join":
                separator = translate_expression(expression.func.value)

                if len(expression.args) == 1:
                    iterable = translate_expression(expression.args[0])
                    return f"{iterable} joined with {separator}"

            if expression.func.attr == "startswith":
                if len(expression.args) == 1:
                    value = translate_expression(expression.func.value)
                    prefix = translate_expression(expression.args[0])
                    return f"{value} starts with {prefix}"

            if expression.func.attr == "isdigit":
                if not expression.args and not expression.keywords:
                    value = translate_expression(expression.func.value)
                    return f"{value} is nonempty and contains only digits"

    if isinstance(expression, ast.Attribute):
        if (
            isinstance(expression.value, ast.Name)
            and expression.value.id == "str"
            and expression.attr == "upper"
        ):
            return "the function that converts a string to uppercase"

    if isinstance(expression, ast.Subscript):
        collection = translate_expression(expression.value)

        if isinstance(expression.slice, ast.Slice):
            if expression.slice.lower is not None and expression.slice.upper is None:
                start = translate_expression(expression.slice.lower)
                return f"the items in {collection} from index {start} onward"

        index = translate_expression(expression.slice)
        return f"the item in {collection} at index ({index})"

    return ast.unparse(expression)


def translate_function_call(call: ast.Call) -> str:
    """Translate a Python function call into plain English."""
    if isinstance(call.func, ast.Attribute):
        if call.func.attr == "sort":
            if not call.args and not call.keywords:
                collection = translate_expression(call.func.value)
                return f"Sort {collection} in place."

        if call.func.attr == "join":
            if len(call.args) == 1:
                separator = translate_expression(call.func.value)
                iterable = translate_expression(call.args[0])
                return f"Join {iterable} with {separator}."

        if call.func.attr == "startswith":
            if len(call.args) == 1:
                value = translate_expression(call.func.value)
                prefix = translate_expression(call.args[0])
                return f"Check whether {value} starts with {prefix}."

    function_name = ast.unparse(call.func)

    arguments: list[str] = []

    for argument in call.args:
        translated_argument = translate_expression(argument)
        arguments.append(translated_argument)

    if not arguments:
        translation = f"Call {function_name}."
    elif len(arguments) == 1:
        translation = f"Call {function_name} with the argument {arguments[0]}."
    else:
        leading_arguments = ", ".join(arguments[:-1])
        translation = (
            f"Call {function_name} with the arguments {leading_arguments} and {arguments[-1]}."
        )

    return translation


def translate_import_from(statement: ast.ImportFrom) -> str:
    """Translate a Python from-import statement into plain English."""
    module = statement.module

    names = [
        alias.name
        for alias in statement.names
    ]

    if len(names) == 1:
        return f"Import {names[0]} from {module}."

    leading_names = ", ".join(names[:-1])

    return (
        f"Import {leading_names} and {names[-1]} "
        f"from {module}."
    )


def translate_assignment(statement: ast.Assign) -> str:
    """Translate a Python assignment into plain English."""
    target = ast.unparse(statement.targets[0])
    value = translate_expression(statement.value)
    return f"Set {target} equal to {value}."


def translate_print_call(call: ast.Call) -> str:
    """Translate a Python print call into plain English."""
    argument = translate_expression(call.args[0])
    return f"Print {argument}."


def translate_function_definition(statement: ast.FunctionDef) -> str:
    """Translate a Python or Python function definition into plain English."""
    parameters: list[str] = []

    for argument in statement.args.args:
        parameters.append(argument.arg)

    if not parameters:
        parameter_description = "no parameters"
    elif len(parameters) == 1:
        parameter_description = f"the parameter {parameters[0]}"
    else:
        leading_parameters = ", ".join(parameters[:-1])
        parameter_description = (
            f"the parameters {leading_parameters} and {parameters[-1]}"
        )

    header = (
        f"Define a function named {statement.name} "
        f"that accepts {parameter_description}."
    )

    translations: list[str] = [header]

    for nested_statement in statement.body:
        nested_translation = translate_statement(nested_statement)
        translations.append(indent_translation(nested_translation))

    return "\n".join(translations)


def translate_for_statement(statement: ast.For) -> str:
    """Translate a Python for loop into plain English."""
    target = ast.unparse(statement.target)
    iterable = translate_expression(statement.iter)
    translations: list[str] = [f"For each {target} in {iterable}:"]

    for nested_statement in statement.body:
        nested_translation = translate_statement(nested_statement)
        translations.append(indent_translation(nested_translation))

    return "\n".join(translations)


def translate_while_statement(statement: ast.While) -> str:
    """Translate a Python while loop into plain English."""
    if not isinstance(statement.test, ast.Compare):
        return "Unsupported while condition."

    condition = translate_condition(statement.test)
    translations: list[str] = [f"While {condition}:"]

    for nested_statement in statement.body:
        nested_translation = translate_statement(nested_statement)
        translations.append(indent_translation(nested_translation))

    return "\n".join(translations)


def translate_augmented_assignment(statement: ast.AugAssign) -> str:
    """Translate a Python augmented assignment into plain English."""
    target = ast.unparse(statement.target)
    value = translate_expression(statement.value)

    if isinstance(statement.op, ast.Add):
        return f"Add {value} to {target}."
    if isinstance(statement.op, ast.Sub):
        return f"Subtract {value} from {target}."
    if isinstance(statement.op, ast.Mult):
        return f"Multiply {target} by {value}."
    if isinstance(statement.op, ast.Div):
        return f"Divide {target} by {value}."
    if isinstance(statement.op, ast.FloorDiv):
        return f"Floor divide {target} by {value}."
    if isinstance(statement.op, ast.Mod):
        return f"Set {target} to {target} modulo {value}."
    if isinstance(statement.op, ast.Pow):
        return f"Raise {target} to the power of {value}."

    return "Unsupported augmented assignment."


def translate_annotated_assignment(statement: ast.AnnAssign) -> str:
    """Translate an annotated Python assignment into plain English."""
    target = ast.unparse(statement.target)

    if statement.value is None:
        annotation = ast.unparse(statement.annotation)
        return f"Declare {target} as {annotation}."

    value = translate_expression(statement.value)

    return f"Set {target} equal to {value}."
        

def translate_statement(statement: ast.stmt) -> str:
    """Translate one Python statement into plain English."""
    if isinstance(statement, ast.ImportFrom):
        return translate_import_from(statement)
    
    if isinstance(statement, ast.Assign):
        return translate_assignment(statement)

    if isinstance(statement, ast.AnnAssign):
        return translate_annotated_assignment(statement)

    if isinstance(statement, ast.FunctionDef):
        return translate_function_definition(statement)

    if isinstance(statement, ast.If):
        return translate_if_statement(statement)

    if isinstance(statement, ast.For):
        return translate_for_statement(statement)

    if isinstance(statement, ast.While):
        return translate_while_statement(statement)

    if isinstance(statement, ast.AugAssign):
        return translate_augmented_assignment(statement)

    if isinstance(statement, ast.Return):
        return translate_return_statement(statement)

    if isinstance(statement, ast.Expr):
        call = statement.value

        if isinstance(call, ast.Call):
            function = call.func

            if isinstance(function, ast.Name) and function.id == "print":
                return translate_print_call(call)

            return translate_function_call(call)

    return "Unsupported statement."


def indent_translation(translation: str) -> str:
    """Indent every line of a translation by four spaces."""
    indented_lines = (
        f"    {line}" for line in translation.splitlines()
    )
    return "\n".join(indented_lines)


def translate_comparison(comparison: ast.Compare) -> str:
    left = translate_expression(comparison.left)
    operator = comparison.ops[0]
    right = translate_expression(comparison.comparators[0])

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


def translate_condition(condition: ast.expr) -> str:
    if isinstance(condition, ast.Compare):
        return translate_comparison(condition)

    if isinstance(condition, ast.Call):
        return translate_expression(condition)

    if isinstance(condition, ast.BoolOp):
        if isinstance(condition.op, ast.And):
            operator = " and "
        elif isinstance(condition.op, ast.Or):
            operator = " or "
        else:
            return "Unsupported boolean operator"

        translated_values = [
            translate_condition(value)
            for value in condition.values
        ]

        return operator.join(translated_values)

    return "Unsupported condition"


def translate_if_statement(statement: ast.If) -> str:
    """Translate a Python if statement into plain English."""
    if not isinstance(
        statement.test,
        (ast.Compare, ast.BoolOp, ast.Call),
    ):
        return "Unsupported if condition"

    condition = translate_condition(statement.test)

    condition = translate_condition(statement.test)
    translations: list[str] = [f"If {condition}:"]

    for nested_statement in statement.body:
        nested_translation = translate_statement(nested_statement)
        translations.append(indent_translation(nested_translation))

    if statement.orelse:
        possible_elif = statement.orelse[0]

        if len(statement.orelse) == 1 and isinstance(possible_elif, ast.If):
            elif_translation = translate_if_statement(possible_elif)
            elif_translation = elif_translation.replace("If ", "Elif ", 1)
            translations.append(elif_translation)
        else:
            translations.append("Else:")
            for nested_statement in statement.orelse:
                nested_translation = translate_statement(nested_statement)
                translations.append(indent_translation(nested_translation))

    return "\n".join(translations)


def translate_return_statement(statement: ast.Return) -> str:
    """Translate a Python return statement into plain English."""
    if statement.value is None:
        return "Return."
    value = translate_expression(statement.value)
    return f"Return {value}."


def translate_python(python_code: str) -> str:
    """Translate Python source code into plain English."""
    tree = ast.parse(python_code)
    translations: list[str] = []

    for statement in tree.body:
        translation = translate_statement(statement)
        translations.append(translation)

    return "\n".join(translations)
