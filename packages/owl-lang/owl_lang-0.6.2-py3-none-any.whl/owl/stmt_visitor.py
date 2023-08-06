from __future__ import annotations
from typing import TYPE_CHECKING, Any, List

from .data_types.owl_function import OwlFunction, OwlReturnValue

if TYPE_CHECKING:
    from .interpreter import Interpreter

from .environment import Environment
from .owl_ast.stmt import VarDeclaration
from .expr_visitor import ExprVisitor
from .owl_ast.stmt import (
    PrintStmt,
    ExpressionStmt,
    Visitor,
    Stmt,
    BlockStmt,
    IfStmt,
    WhileStmt,
    FunctionDeclaration,
    ReturnStmt,
)


def stringify(value: Any) -> str:
    if value is None:
        return "nil"
    text = str(value)
    if isinstance(value, float):
        if text.endswith(".0"):
            text = text[:-2]
    elif isinstance(value, bool):
        text = text.lower()

    return text


class StmtVisitor(Visitor):
    interpreter: Interpreter
    expr_visitor: ExprVisitor

    def __init__(self, expr_visitor: ExprVisitor, interpreter: Interpreter):
        self.expr_visitor = expr_visitor
        self.interpreter = interpreter

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self.expr_visitor.evaluate(stmt.expression)

    def visit_print_stmt(self, stmt: PrintStmt) -> None:
        value = self.expr_visitor.evaluate(stmt.expression)
        print(stringify(value))

    def visit_var_declaration(self, stmt: VarDeclaration) -> None:
        init_value = None
        if stmt.initializer:
            init_value = self.expr_visitor.evaluate(stmt.initializer)
        # define variable in the environment
        self.interpreter.define_variable(stmt.name.lexeme, init_value)

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        block_environment = Environment(self.interpreter.curr_environment)
        self.execute_block(stmt.statements, block_environment)

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        value = self.expr_visitor.evaluate(stmt.condition)
        if bool(value):
            self.execute(stmt.then_branch)
        elif stmt.else_branch is not None:
            self.execute(stmt.else_branch)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        condition_value = self.expr_visitor.evaluate(stmt.condition)
        while condition_value:
            self.execute(stmt.body)
            condition_value = self.expr_visitor.evaluate(stmt.condition)

    def visit_function_declaration(self, stmt: FunctionDeclaration) -> None:
        fun_name = stmt.name.lexeme
        # capture current environment as function close
        closure = self.interpreter.curr_environment
        function = OwlFunction(declaration=stmt, closure=closure)
        # define function in the environment
        self.interpreter.define_variable(fun_name, function)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        value = None
        if stmt.value is not None:
            value = self.expr_visitor.evaluate(stmt.value)
        raise OwlReturnValue(value)

    def execute_block(self, statements: List[Stmt], block_env: Environment):
        previous = self.interpreter.curr_environment
        try:
            self.interpreter.curr_environment = block_env
            for stmt in statements:
                self.execute(stmt)
        finally:
            self.interpreter.curr_environment = previous

    def execute(self, stmt: Stmt):
        stmt.accept(self)
