from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .interpreter import Interpreter

from .owl_ast.expr import Assignment
from .owl_ast.expr import Variable
from .owl_ast.expr import (
    Unary,
    Literal,
    Grouping,
    Binary,
    Logical,
    FunctionCall,
    Ternary,
)
from .owl_token import Token
from .token_type import TokenType
from .owl_ast.expr import Visitor, Expr
from .owl_error import OwlRuntimeError
from .data_types.owl_function import OwlCallable


def check_number_operand(operator: Token, operand) -> None:
    if isinstance(operand, float):
        return
    raise OwlRuntimeError(operator, "Operand must be a number.")


def check_number_operands(operator: Token, left, right) -> None:
    if isinstance(left, float) and isinstance(right, float):
        return
    raise OwlRuntimeError(operator, "Operands must be numbers.")


def check_number_or_string_operands(operator: Token, left, right) -> None:
    is_number = isinstance(left, float) and isinstance(right, float)
    is_string = isinstance(left, str) and isinstance(right, str)
    if is_number or is_string:
        return
    raise OwlRuntimeError(operator, "Operands must be numbers or strings.")


class ExprVisitor(Visitor):
    interpreter: Interpreter

    def __init__(self, interpreter: Interpreter):
        self.interpreter = interpreter

    def visit_binary_expr(self, expr: Binary):
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        op_type = expr.operator.type
        if op_type == TokenType.MINUS:
            check_number_operands(expr.operator, left, right)
            return left - right
        elif op_type == TokenType.PLUS:
            # TODO - check type
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            elif isinstance(left, float) and isinstance(right, float):
                return left + right
            elif isinstance(left, float) and isinstance(right, str):
                return str(left) + right
            elif isinstance(left, str) and isinstance(right, float):
                return left + str(right)
            else:
                raise OwlRuntimeError(expr.operator, "Cannot perform PLUS operator.")
        elif op_type == TokenType.SLASH:
            check_number_operands(expr.operator, left, right)
            return left / right
        elif op_type == TokenType.STAR:
            check_number_operands(expr.operator, left, right)
            return left * right
        elif op_type == TokenType.GREATER:
            check_number_operands(expr.operator, left, right)
            return left > right
        elif op_type == TokenType.GREATER_EQUAL:
            check_number_operands(expr.operator, left, right)
            return left >= right
        elif op_type == TokenType.LESS:
            check_number_operands(expr.operator, left, right)
            return left < right
        elif op_type == TokenType.LESS_EQUAL:
            check_number_operands(expr.operator, left, right)
            return left <= right
        elif op_type == TokenType.BANG_EQUAL:
            check_number_or_string_operands(expr.operator, left, right)
            return not self.is_equal(left, right)
        elif op_type == TokenType.EQUAL_EQUAL:
            check_number_or_string_operands(expr.operator, left, right)
            return self.is_equal(left, right)

        # unreachable
        return None

    def visit_grouping_expr(self, expr: Grouping):
        return self.evaluate(expr.expression)

    def visit_literal_expr(self, expr: Literal):
        return expr.value

    def visit_unary_expr(self, expr: Unary):
        right = self.evaluate(expr.right)
        op_type = expr.operator.type
        if op_type == TokenType.BANG:
            return not bool(right)
        elif op_type == TokenType.MINUS:
            check_number_operand(expr.operator, right)
            return -right
        # unreachable
        return None

    def visit_variable_expr(self, expr: Variable):
        name: Token = expr.name
        return self.interpreter.lookup_variable(expr)

    def visit_assignment_expr(self, expr: Assignment):
        value = self.evaluate(expr.value)
        self.interpreter.assign_variable(expr.name, value)
        return value

    def visit_logical_expr(self, expr: Logical):
        left_value = self.evaluate(expr.left)
        if expr.operator.type == TokenType.OR:
            if bool(left_value):
                return left_value
        else:
            if not bool(left_value):
                return left_value

        return self.evaluate(expr.right)

    def visit_functioncall_expr(self, expr: FunctionCall):
        callee = self.evaluate(expr.callee)
        arguments = []
        for argument in expr.arguments:
            arg_value = self.evaluate(argument)
            arguments.append(arg_value)
        if not isinstance(callee, OwlCallable):
            raise OwlRuntimeError(expr.paren, "Object is not callable.")
        if len(arguments) != callee.arity():
            raise OwlRuntimeError(
                expr.paren,
                f"Expect {callee.arity()} arguments but got {len(arguments)}.",
            )
        return callee.call(self.interpreter, arguments)

    def visit_ternary_expr(self, expr: Ternary):
        condition_value = self.evaluate(expr.condition)
        if condition_value:
            then_value = self.evaluate(expr.thenExpr)
            return then_value
        else:
            else_value = self.evaluate(expr.elseExpr)
            return else_value

    def evaluate(self, expr: Expr):
        return expr.accept(self)

    def is_equal(self, left, right):
        return left == right
