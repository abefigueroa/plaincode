"""Application entry point and workflow."""
from .python_to_english import translate_python


# Functions
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
    print("1. Python to plain English")
    print("2. Plain English to Python")
    print("3. Exit")

    choice = input("Choose an option: ")
    if choice == "1":
        print("Enter Python code and type END when finished")
        python_code = collect_multiline_input()
        translation = translate_python(python_code)
        print(translation)
    elif choice == "2":
        print("Enter plain English and type END when finished.")
        plain_english = collect_multiline_input()
        print(plain_english)
    elif choice == "3":
        print("Goodbye!")
    else:
        print("invalid option.")

if __name__ == "__main__":
    main()