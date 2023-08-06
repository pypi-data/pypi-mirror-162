from __future__ import annotations
from typing import List
from .token_type import TokenType
from dataclasses import dataclass


class OwlError(Exception):
    def __init__(self, token, message):
        # Call the base class constructor with the parameters it needs
        super().__init__(message)
        self.token = token
        self.message = message
        self.type = "OwlError"

    def __str__(self):
        line = self.token.line
        lexeme = self.token.lexeme
        if self.token.type == TokenType.EOF:
            return f"[Line {line}] {self.type} at end: {self.message}"
        else:
            return f"[Line {line}] {self.type} at '{lexeme}': {self.message}"


class ParseError(OwlError):
    def __init__(self, token, message):
        super().__init__(token, message)
        self.type = "ParseError"


class OwlRuntimeError(OwlError):
    def __init__(self, token, message):
        super().__init__(token, message)
        self.type = "RuntimeError"


class ResolverError(OwlError):
    def __init__(self, token, message):
        super().__init__(token, message)
        self.type = "ResolverError"


class LexingError(Exception):
    line: int
    message: str
    position_in_line: int

    def __init__(self, line, message, position_in_line):
        super().__init__(message)
        self.line = line
        self.message = message
        self.position_in_line = position_in_line

    def __str__(self):
        return f"[Line {self.line}] LexingError: {self.message}"


class ErrorPrinter:
    lines: List[str]

    def __init__(self, source: str):
        self.lines = source.split("\n")

    def print_errors(self, errors: List[OwlError]):
        for error in errors:
            self.print_error(error)

    def print_lexing_error(self, error: LexingError):
        print(error)
        line = error.line
        line_pos = error.position_in_line
        print(self.lines[line])
        print(" " * (line_pos - 1), "^" * 1)

    def print_error(self, error: OwlError):
        if isinstance(error, LexingError):
            self.print_lexing_error(error)
            return

        error_str = str(error)
        print(error_str)

        line = error.token.line
        line_pos = error.token.position_in_line
        lexeme = error.token.lexeme
        print(self.lines[line])
        print(" " * (line_pos - 1), "^" * len(lexeme))
