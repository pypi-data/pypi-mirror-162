from dataclasses import dataclass
from .token_type import TokenType
from typing import Any


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    literal: Any
    line: int
    position_in_line: int
