from __future__ import annotations
from dataclasses import dataclass
from owl.owl_token import Token
from typing import Any
from abc import ABC, abstractmethod
from typing import List


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor):
        pass


@dataclass(frozen=True)
class Assignment(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_assignment_expr(self)


@dataclass(frozen=True)
class Ternary(Expr):
    condition: Expr
    thenExpr: Expr
    elseExpr: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_ternary_expr(self)


@dataclass(frozen=True)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_logical_expr(self)


@dataclass(frozen=True)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_binary_expr(self)


@dataclass(frozen=True)
class FunctionCall(Expr):
    callee: Expr
    paren: Token
    arguments: List[Expr]

    def accept(self, visitor: Visitor):
        return visitor.visit_functioncall_expr(self)


@dataclass(frozen=True)
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_grouping_expr(self)


@dataclass(frozen=True)
class Literal(Expr):
    value: Any

    def accept(self, visitor: Visitor):
        return visitor.visit_literal_expr(self)


@dataclass(frozen=True)
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_unary_expr(self)


@dataclass(frozen=True)
class Variable(Expr):
    name: Token

    def accept(self, visitor: Visitor):
        return visitor.visit_variable_expr(self)


class Visitor(ABC):
    @abstractmethod
    def visit_assignment_expr(self, expr: Assignment):
        pass

    @abstractmethod
    def visit_ternary_expr(self, expr: Ternary):
        pass

    @abstractmethod
    def visit_logical_expr(self, expr: Logical):
        pass

    @abstractmethod
    def visit_binary_expr(self, expr: Binary):
        pass

    @abstractmethod
    def visit_functioncall_expr(self, expr: FunctionCall):
        pass

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping):
        pass

    @abstractmethod
    def visit_literal_expr(self, expr: Literal):
        pass

    @abstractmethod
    def visit_unary_expr(self, expr: Unary):
        pass

    @abstractmethod
    def visit_variable_expr(self, expr: Variable):
        pass
