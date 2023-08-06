from __future__ import annotations
from typing import List, Any, Dict, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .owl_ast.expr import Expr, Variable, Assignment

import logging

logger = logging.getLogger(__name__)

from .owl_token import Token
from .owl_ast.stmt import Stmt
from .expr_visitor import ExprVisitor
from .stmt_visitor import StmtVisitor
from .environment import Environment
from .owl_error import OwlRuntimeError
from .native_functions import ClockFunction, NumberFunction, InputFunction


class Interpreter:
    expr_visitor: ExprVisitor
    stmt_visitor: StmtVisitor
    runtime_errors: List[OwlRuntimeError]
    curr_environment: Environment
    global_environment: Environment

    # store resolution information
    resolved_local_variables: Dict[Expr, int]

    def __init__(self):
        self.global_environment = Environment()
        self.curr_environment = self.global_environment
        self.define_native_function()
        self.expr_visitor = ExprVisitor(self)
        self.stmt_visitor = StmtVisitor(self.expr_visitor, self)
        self.runtime_errors = []
        self.resolved_local_variables = {}

    def resolve(self, expr: Union[Variable, Assignment], depth: int):
        """
        Tell interpreter how many scopes there are between the current scope
        and the scope where the variable is defined
        """
        self.resolved_local_variables[expr] = depth

    def interpret(self, statements: List[Stmt]):
        try:
            for stmt in statements:
                self.stmt_visitor.execute(stmt)
        except OwlRuntimeError as runtime_error:
            self.runtime_errors.append(runtime_error)
            print(runtime_error)

    def assign_variable(self, name: Token, value: Any):
        self.curr_environment.assign(name, value)

    # def get_variable(self, name: Token):
    #     return self.curr_environment.get(name)

    def lookup_variable(self, expr: Variable):
        distance = self.resolved_local_variables.get(expr)
        if distance is not None:
            return self.curr_environment.get_at(distance, expr.name)
        else:
            return self.global_environment.get(expr.name)

    def define_variable(self, name: str, value: Any):
        """
        Bind a name to a value at current environment
        """
        self.curr_environment.define(name, value)

    def define_native_function(self):
        clock_function = ClockFunction()
        number_function = NumberFunction()
        input_function = InputFunction()
        self.global_environment.define("clock", clock_function)
        self.global_environment.define("number", number_function)
        self.global_environment.define("input", input_function)
