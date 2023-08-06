from __future__ import annotations
from typing import Dict, Any, Optional
from .owl_error import OwlRuntimeError
from .owl_token import Token


class Environment:
    enclosing: Optional[Environment]
    values: Dict[str, Any]

    def __init__(self, enclosing: Optional[Environment] = None):
        self.values = {}
        self.enclosing = enclosing

    def define(self, name: str, value: Any):
        # Bind a new name to a value, aka declaration + initialization
        self.values[name] = value

    def assign(self, name: Token, value: Any):
        if name.lexeme in self.values:
            self.values[name.lexeme] = value
            return
        if self.enclosing is not None:
            self.enclosing.assign(name, value)
            return
        raise OwlRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get(self, name: Token):
        if name.lexeme in self.values:
            return self.values[name.lexeme]
        # if self.enclosing is not None:
        #     return self.enclosing.get(name)
        raise OwlRuntimeError(name, f"Undefined variable '{name.lexeme}'.")

    def get_at(self, distance: int, name: Token):
        environment = self
        # walk through a fixed number of hops up the parent chain
        for i in range(distance):
            environment = environment.enclosing

        return environment.get(name)
