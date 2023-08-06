from __future__ import annotations
from typing import TYPE_CHECKING
from owl.owl_ast.expr import (
    Variable,
    Unary,
    Literal,
    Grouping,
    FunctionCall,
    Binary,
    Logical,
    Ternary,
    Assignment,
    Expr,
)
from owl.owl_ast.expr import Visitor
from owl.owl_error import ResolverError

if TYPE_CHECKING:
    from .resolver import Resolver


class ExprResolver(Visitor):
    resolver: Resolver

    def __init__(self, resolver: Resolver):
        self.resolver = resolver

    def resolve_expr(self, expr: Expr):
        expr.accept(self)

    def visit_assignment_expr(self, expr: Assignment):
        self.resolve_expr(expr.value)
        self.resolver.resolve_local(expr)

    def visit_ternary_expr(self, expr: Ternary):
        self.resolve_expr(expr.condition)
        self.resolve_expr(expr.thenExpr)
        self.resolve_expr(expr.elseExpr)

    def visit_logical_expr(self, expr: Logical):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_binary_expr(self, expr: Binary):
        self.resolve_expr(expr.left)
        self.resolve_expr(expr.right)

    def visit_functioncall_expr(self, expr: FunctionCall):
        self.resolve_expr(expr.callee)
        for argument in expr.arguments:
            self.resolve_expr(argument)

    def visit_grouping_expr(self, expr: Grouping):
        self.resolve_expr(expr.expression)

    def visit_literal_expr(self, expr: Literal):
        """
        Literal doesn't mention any variables so there is no work to do
        """
        pass

    def visit_unary_expr(self, expr: Unary):
        self.resolve_expr(expr.right)

    def visit_variable_expr(self, expr: Variable):
        if len(self.resolver.scopes) > 0:
            # TODO - Why check len
            inner_most = self.resolver.scopes[-1]
            initialized = inner_most.get(expr.name.lexeme)
            if initialized == False:
                # Variable has been declared but not yet defined
                raise ResolverError(
                    expr.name, "Can't read local variable in its own initializer."
                )
        # resolve actual variable using this helper
        self.resolver.resolve_local(expr)
