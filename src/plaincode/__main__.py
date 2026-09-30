"""Application entry point and workflow."""

from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer

from plaincode.english_to_python import (
    UnsupportedEnglishError,
    guess_statement,
    translate_english,
)
from plaincode.python_explainer import explain_python
from plaincode.python_to_english import translate_python
from plaincode.python_transform import (
    break_apart_python,
    combine_python,
)


def print_python(code: str) -> None:
    """Print Python code with terminal syntax highlighting."""
    highlighted_code = highlight(
        code,
        PythonLexer(),
        TerminalFormatter(),
    )

    print(highlighted_code, end="")


def collect_multiline_input() -> tuple[str, str]:
    """Collect multiline input until a PlainCode command is entered."""
    lines: list[str] = []

    while True:
        line = input()
        command = line.upper()

        if command == "HELP":
            print("Available commands:")
            print("END = translate")
            print("EXPLAIN = explain what the code does")
            print("BREAK_APART = expand nested code")
            print("COMBINE = combine intermediate steps")
            print("MENU = return to the main menu")
            continue

        if command in {
            "END",
            "EXPLAIN",
            "BREAK_APART",
            "COMBINE",
            "MENU",
        }:
            return "\n".join(lines), command

        lines.append(line)


def main() -> None:
    """Run the PlainCode terminal application."""
    while True:
        print("\nPlainCode")
        print("1. Python to English")
        print("2. English to Python")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            print("Enter Python code. Type HELP for commands.")
            python_code, command = collect_multiline_input()

            if command == "MENU":
                continue

            try:
                if command == "END":
                    print(translate_python(python_code))

                elif command == "EXPLAIN":
                    print(explain_python(python_code))

                elif command == "BREAK_APART":
                    transformed_code = break_apart_python(python_code)
                    print_python(transformed_code)

                elif command == "COMBINE":
                    transformed_code = combine_python(python_code)
                    print_python(transformed_code)

            except SyntaxError as error:
                print(
                    f"Invalid Python syntax on line {error.lineno}: "
                    f"{error.msg}"
                )

        elif choice == "2":
            print("Enter plain English. Type HELP for commands.")
            plain_english, command = collect_multiline_input()

            if command == "MENU":
                continue

            translations: list[str] = []

            for line in plain_english.splitlines():
                try:
                    translation = translate_english(line)
                    translations.append(translation)

                except UnsupportedEnglishError:
                    guess = guess_statement(line)

                    if guess is None:
                        print(
                            f"PlainCode could not understand: {line}"
                        )
                        break

                    print(f"Did you mean: {guess}")
                    confirmation = input(
                        "Use this interpretation? (y/n): "
                    )

                    if confirmation.lower() == "y":
                        try:
                            translations.append(
                                translate_english(guess)
                            )
                        except UnsupportedEnglishError as error:
                            print(
                                f"PlainCode could not translate "
                                f"that interpretation: {error}"
                            )
                            break
                    else:
                        print(
                            "Please try entering your English again."
                        )
                        break

            else:
                python_code = "\n".join(translations)
                print_python(python_code)

        elif choice == "3":
            print("Goodbye!")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()