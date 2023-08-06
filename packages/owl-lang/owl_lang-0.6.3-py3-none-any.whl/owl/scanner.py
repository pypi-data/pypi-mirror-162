from typing import List, Dict, Optional
from .owl_token import Token
from .token_type import TokenType
from .owl_error import LexingError


class Scanner:
    source: str
    tokens: List[Token]

    start: int
    current: int
    line: int
    line_start: int
    token_map: Dict[str, TokenType]
    keywords: Dict[str, TokenType]

    lexing_error: Optional[LexingError]

    def __init__(self, source: str):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 0
        self.line_start = 0
        self.source_len = len(source)
        self.lexing_error = None

        self.token_map = {
            "(": TokenType.LEFT_PAREN,
            ")": TokenType.RIGHT_PAREN,
            "{": TokenType.LEFT_BRACE,
            "}": TokenType.RIGHT_BRACE,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            "-": TokenType.MINUS,
            "+": TokenType.PLUS,
            ";": TokenType.SEMICOLON,
            "*": TokenType.STAR,
            "?": TokenType.QUESTION,
            ":": TokenType.COLON,
        }

        self.keywords = {
            "and": TokenType.AND,
            "class": TokenType.CLASS,
            "else": TokenType.ELSE,
            "false": TokenType.FALSE,
            "for": TokenType.FOR,
            "fun": TokenType.FUN,
            "if": TokenType.IF,
            "nil": TokenType.NIL,
            "or": TokenType.OR,
            "print": TokenType.PRINT,
            "super": TokenType.SUPER,
            "return": TokenType.RETURN,
            "this": TokenType.THIS,
            "true": TokenType.TRUE,
            "var": TokenType.VAR,
            "while": TokenType.WHILE,
        }

    def scan_tokens(self) -> List[Token]:
        try:
            while not self.is_at_end():
                # we are at the beginning of the next lexeme
                self.start = self.current
                self.scan_token()

            eof_token = Token(
                TokenType.EOF, "", None, self.line, position_in_line=self.current
            )
            self.tokens.append(eof_token)
            return self.tokens
        except LexingError as error:
            self.lexing_error = error

    def scan_token(self):
        c = self.advance()

        if c in self.token_map.keys():
            token_type = self.token_map[c]
            self.add_token(token_type, literal=None)
        elif c == "!":
            # for some operators, need to look at the second character
            token_type = TokenType.BANG_EQUAL if self.match("=") else TokenType.BANG
            self.add_token(token_type, literal=None)
        elif c == "=":
            token_type = TokenType.EQUAL_EQUAL if self.match("=") else TokenType.EQUAL
            self.add_token(token_type, literal=None)
        elif c == "<":
            token_type = TokenType.LESS_EQUAL if self.match("=") else TokenType.LESS
            self.add_token(token_type, literal=None)
        elif c == ">":
            token_type = (
                TokenType.GREATER_EQUAL if self.match("=") else TokenType.GREATER
            )
            self.add_token(token_type, literal=None)
        elif c == "/":
            if self.match("/"):
                # A comment goes until the end of line
                while self.peek() != "\n" and not self.is_at_end():
                    self.advance()
            else:
                self.add_token(TokenType.SLASH, literal=None)
        elif c in [" ", "\r", "\t"]:
            # do nothing
            pass
        elif c == "\n":
            self.line += 1
            self.line_start = self.current
        elif c == '"':
            self.string()
        else:
            if c.isdigit():
                self.number()
            elif c.isalpha():
                self.identifier()
            else:
                raise LexingError(
                    self.line,
                    "Unexpected character.",
                    position_in_line=self.start - self.line_start,
                )

    def identifier(self):
        while self.peek().isalnum():
            self.advance()

        text = self.source[self.start : self.current]
        if text in self.keywords.keys():
            type = self.keywords[text]
            self.add_token(type, literal=None)
        else:
            self.add_token(TokenType.IDENTIFIER, literal=None)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        # Look for a fractional part
        if self.peek() == "." and self.peek_next().isdigit():
            # consume the "."
            self.advance()

            while self.peek().isdigit():
                self.advance()

        value = float(self.source[self.start : self.current])
        self.add_token(TokenType.NUMBER, value)

    def add_token(self, token_type: TokenType, literal):
        lexeme = self.source[self.start : self.current]
        position_in_line = self.start - self.line_start
        token = Token(token_type, lexeme, literal, self.line, position_in_line)
        self.tokens.append(token)

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False

        # advance
        self.current += 1
        return True

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == "\n":
                self.line += 1
            self.advance()

        if self.is_at_end():
            raise LexingError(
                self.line,
                "Unterminated string.",
                position_in_line=self.current - self.line_start,
            )

        # the closing "
        self.advance()

        value = self.source[self.start + 1 : self.current - 1]
        self.add_token(TokenType.STRING, value)

    def advance(self):
        char = self.source[self.current]
        self.current += 1
        return char

    def peek(self):
        if self.is_at_end():
            return "\x00"
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= self.source_len:
            return "\x00"
        return self.source[self.current + 1]

    def is_at_end(self):
        return self.current >= self.source_len
