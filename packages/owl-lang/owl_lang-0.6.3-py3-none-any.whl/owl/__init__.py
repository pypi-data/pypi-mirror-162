import sys
from .scanner import Scanner
from .parser import Parser
from .interpreter import Interpreter
from pathlib import Path
from .resolver.resolver import Resolver


def runFile(path: str, interpreter: Interpreter):
    source_file = Path(path)
    if not source_file.exists():
        print(f"[RuntimeError]: Can't open file '{source_file}'. No such file or directory.")
        return
    source = source_file.read_text(encoding="utf-8")
    run(source, interpreter)


def runPrompt(interpreter: Interpreter):
    print(f"Welcome to The owl 🦉 programming language v0.6.3.")
    print('Type ".help" for more information. Type ".exit" to exit.')
    while True:
        try:
            line = input("> ")
            if len(line) == 0:
                break
            if line == ".exit":
                break
            run(line, interpreter)
        except (KeyboardInterrupt, EOFError):
            sys.exit(0)


def run(source: str, interpreter: Interpreter):
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    # terminate if there are any scan errors
    if scanner.lexing_error is not None:
        print(scanner.lexing_error)
        return

    parser = Parser(tokens)
    statements = parser.parse()
    # terminate if there are any parse error
    if len(parser.parse_errors) > 0:
        for error in parser.parse_errors:
            print(error)
        return

    resolver = Resolver(interpreter)
    resolver.resolve(statements)
    interpreter.interpret(statements)


def main():
    n = len(sys.argv) - 1
    interpreter = Interpreter()
    if n > 1:
        print("Usage: owl [script]")
    elif n == 1:
        runFile(sys.argv[1], interpreter)
    else:
        runPrompt(interpreter)
