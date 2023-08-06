from dataclasses import dataclass
from .owl_token import Token
from .token_type import TokenType


@dataclass
class OwlErrorMessage:
    token: Token
    message: str

    def __str__(self):
        line = self.token.line
        lexeme = self.token.lexeme
        if self.token.type == TokenType.EOF:
            return f"[Line {line}] Error at end: {self.message}"
        else:
            return f"[Line {line}] Error at '{lexeme}': {self.message}"
