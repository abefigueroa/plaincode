"""Application entry point and workflow."""
from .python_to_english import translate_python
from plaincode.english_to_python import (
    UnsupportedEnglishError,
    guess_statement,
    translate_english,
)
from plaincode.python_transform import (
    break_apart_python,
    combine_python,
)


def collect_multiline_input() -> tuple[str, str]:
    """Collect multiline input until a PlainCode command is entered."""
    lines: list[str] = []

    while True:
        line = input()
        command = line.upper()

        if command in {
            "END",
            "EXPLAIN",
            "BREAK_APART",
            "COMBINE",
        }:
            return "\n".join(lines), command

        lines.append(line)

        
def main() -> None:
    """Run the PlainCode terminal application."""
    print("PlainCode")
    print("1. Python to English")
    print("2. English to Python")
    print("3. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        print(
            "Enter Python code.\n"
            "END = translate\n"
            "BREAK_APART = expand nested code"
        )

        python_code, command = collect_multiline_input()

        try:
            if command == "END":
                print(translate_python(python_code))

            elif command == "BREAK_APART":
                print(break_apart_python(python_code))

            elif command == "EXPLAIN":
                print("EXPLAIN is not implemented yet.")

            elif command == "COMBINE":
                print(combine_python(python_code))

        except SyntaxError as error:
            print(
                f"Invalid Python syntax on line {error.lineno}: "
                f"{error.msg}"
            )

    elif choice == "2":
        print("Enter plain English and type END when finished.")
        plain_english, command = collect_multiline_input()

        translations: list[str] = []

        for line in plain_english.splitlines():
            try:
                translation = translate_english(line)
                translations.append(translation)

            except UnsupportedEnglishError:
                guess = guess_statement(line)

                if guess is None:
                    print(f"PlainCode could not understand: {line}")
                    return

                print(f"Did you mean: {guess}")
                confirmation = input("Use this interpretation? (y/n): ")

                if confirmation.lower() == "y":
                    translations.append(translate_english(guess))
                else:
                    print("Please try entering your English again.")
                    return

        print("\n".join(translations))

    elif choice == "3":
        print("Goodbye!")

    else:
        print("Invalid option.")


if __name__ == "__main__":
    main()