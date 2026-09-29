"""Python-to-Python transformation tools."""

import ast
import copy


class BreakApartTransformer(ast.NodeTransformer):
    """Break nested function calls into intermediate steps."""

    def __init__(self) -> None:
        self.step_number = 1

    def next_step_name(self) -> str:
        """Return the next intermediate variable name."""
        step_name = f"step_{self.step_number}"
        self.step_number += 1
        return step_name

    def break_apart_call(
        self,
        call: ast.Call,
        assignments: list[ast.stmt],
    ) -> ast.Name:
        """Break a nested function call into assignments."""
        translated_arguments: list[ast.expr] = []

        for argument in call.args:
            if isinstance(argument, ast.Call):
                translated_argument = self.break_apart_call(
                    argument,
                    assignments,
                )
                translated_arguments.append(translated_argument)
            else:
                translated_arguments.append(argument)

        rebuilt_call = ast.Call(
            func=call.func,
            args=translated_arguments,
            keywords=call.keywords,
        )

        step_name = self.next_step_name()

        assignment = ast.Assign(
            targets=[
                ast.Name(
                    id=step_name,
                    ctx=ast.Store(),
                )
            ],
            value=rebuilt_call,
        )

        assignments.append(assignment)

        return ast.Name(
            id=step_name,
            ctx=ast.Load(),
        )

    def visit_Return(
        self,
        node: ast.Return,
    ) -> ast.Return | list[ast.stmt]:
        """Break apart nested calls inside a return statement."""
        if not isinstance(node.value, ast.Call):
            return node

        calls = [
            child
            for child in ast.walk(node.value)
            if isinstance(child, ast.Call)
        ]

        if len(calls) < 2:
            return node

        assignments: list[ast.stmt] = []

        result = self.break_apart_call(
            node.value,
            assignments,
        )

        return [
            *assignments,
            ast.Return(value=result),
        ]


def break_apart_python(python_code: str) -> str:
    """Break nested Python expressions into intermediate steps."""
    tree = ast.parse(python_code)

    transformer = BreakApartTransformer()
    transformed_tree = transformer.visit(tree)

    ast.fix_missing_locations(transformed_tree)

    return ast.unparse(transformed_tree)

def count_name_uses(node: ast.AST, name: str) -> int:
    """Count how many times a variable is read inside an AST node."""
    return sum(
        1
        for child in ast.walk(node)
        if (
            isinstance(child, ast.Name)
            and isinstance(child.ctx, ast.Load)
            and child.id == name
        )
    )

class NameReplacer(ast.NodeTransformer):
    """Replace one variable reference with an expression."""

    def __init__(
        self,
        variable_name: str,
        replacement: ast.expr,
    ) -> None:
        self.variable_name = variable_name
        self.replacement = replacement

    def visit_Name(self, node: ast.Name) -> ast.expr:
        if (
            isinstance(node.ctx, ast.Load)
            and node.id == self.variable_name
        ):
            return copy.deepcopy(self.replacement)

        return node

def replace_name(
    expression: ast.expr,
    variable_name: str,
    replacement: ast.expr,
) -> ast.expr:
    """Replace a variable inside an expression."""
    replacer = NameReplacer(
        variable_name,
        replacement,
    )

    return replacer.visit(copy.deepcopy(expression))

def is_simple_assignment(statement: ast.stmt) -> bool:
    """Check whether a statement assigns to one simple variable."""
    return (
        isinstance(statement, ast.Assign)
        and len(statement.targets) == 1
        and isinstance(statement.targets[0], ast.Name)
    )

def assignment_target(statement: ast.Assign) -> str:
    """Return the variable name targeted by an assignment."""
    target = statement.targets[0]

    if not isinstance(target, ast.Name):
        raise ValueError("Expected a simple variable assignment.")

    return target.id

class CombineTransformer(ast.NodeTransformer):
    """Combine intermediate assignment chains into nested expressions."""

    def combine_body(
        self,
        body: list[ast.stmt],
    ) -> list[ast.stmt]:
        assignment_counts: dict[str, int] = {}

        for statement in body:
            if is_simple_assignment(statement):
                assignment = statement

                if not isinstance(assignment, ast.Assign):
                    continue

                name = assignment_target(assignment)

                assignment_counts[name] = (
                    assignment_counts.get(name, 0) + 1
                )

        index = 0

        while index < len(body):
            statement = body[index]

            if (
                not isinstance(statement, ast.Return)
                or not isinstance(statement.value, ast.Name)
            ):
                index += 1
                continue

            returned_name = statement.value.id
            current_name = returned_name

            chain: list[ast.Assign] = []
            chain_start = index

            previous_index = index - 1

            while previous_index >= 0:
                previous_statement = body[previous_index]

                if not is_simple_assignment(previous_statement):
                    break

                if not isinstance(previous_statement, ast.Assign):
                    break

                target_name = assignment_target(
                    previous_statement
                )

                if target_name != current_name:
                    break

                if assignment_counts.get(target_name) != 1:
                    break

                chain.append(previous_statement)
                chain_start = previous_index

                earlier_index = previous_index - 1

                if earlier_index < 0:
                    break

                earlier_statement = body[earlier_index]

                if not is_simple_assignment(earlier_statement):
                    break

                if not isinstance(earlier_statement, ast.Assign):
                    break

                earlier_name = assignment_target(
                    earlier_statement
                )

                if count_name_uses(
                    previous_statement.value,
                    earlier_name,
                ) != 1:
                    break

                if not isinstance(
                    previous_statement.value,
                    ast.Call,
                ):
                    break

                nested_calls = [
                    child
                    for child in ast.walk(
                        previous_statement.value
                    )
                    if isinstance(child, ast.Call)
                ]

                if len(nested_calls) != 1:
                    break

                current_name = earlier_name
                previous_index -= 1

            if not chain:
                index += 1
                continue

            chain.reverse()

            expression = copy.deepcopy(chain[0].value)
            current_name = assignment_target(chain[0])

            for assignment in chain[1:]:
                expression = replace_name(
                    assignment.value,
                    current_name,
                    expression,
                )

                current_name = assignment_target(assignment)

            combined_return = ast.Return(
                value=expression,
            )

            body[chain_start:index + 1] = [
                combined_return
            ]

            index = chain_start + 1

        return body

    def visit_FunctionDef(
        self,
        node: ast.FunctionDef,
    ) -> ast.FunctionDef:
        self.generic_visit(node)
        node.body = self.combine_body(node.body)
        return node

    def visit_Module(
        self,
        node: ast.Module,
    ) -> ast.Module:
        self.generic_visit(node)
        node.body = self.combine_body(node.body)
        return node

def combine_python(python_code: str) -> str:
    """Combine intermediate Python steps into nested expressions."""
    tree = ast.parse(python_code)

    transformer = CombineTransformer()
    transformed_tree = transformer.visit(tree)

    ast.fix_missing_locations(transformed_tree)

    return ast.unparse(transformed_tree)