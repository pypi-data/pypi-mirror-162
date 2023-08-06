import sys
from .scanner import Scanner
from .parser import Parser
from .interpreter import Interpreter
from pathlib import Path
from .resolver.resolver import Resolver


def runFile(path: str, interpreter: Interpreter):
    source_file = Path(path)
    if not source_file.exists():
        print("FileNotFound")
    source = source_file.read_text(encoding="utf-8")
    run(source, interpreter)


def runPrompt(interpreter: Interpreter):
    print(f"The owl 🦉 programming language (v0.6.1)")
    print("Inspired by Bob Nystroms's lox and Python.")
    while True:
        line = input("> ")
        if len(line) == 0:
            break

        run(line, interpreter)


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
