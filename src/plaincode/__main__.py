"""Application entry point and workflow."""
from .python_to_english import translate_python

from plaincode.english_to_python import (
    UnsupportedEnglishError,
    guess_statement,
    translate_english,
)


def collect_multiline_input() -> str:
    """Collect lines until the user enters END."""
    lines: list[str] = []

    while True:
        line = input()

        if line.lower() == 'end':
            break
        
        lines.append(line)

    return "\n".join(lines)

        
def main() -> None:
    """Run the PlainCode terminal application."""
    print("PlainCode")
    print("1. Python to English")
    print("2. English to Python")
    print("3. Exit")

    choice = input("Choose an option: ")

    if choice == "1":
        print("Enter Python code and type END when finished")
        python_code = collect_multiline_input()

        try:
            print(translate_python(python_code))
        except SyntaxError as error:
            print(
                f"Invalid Python syntax on line {error.lineno}: "
                f"{error.msg}"
            )

    elif choice == "2":
        print("Enter plain English and type END when finished.")
        plain_english = collect_multiline_input()

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