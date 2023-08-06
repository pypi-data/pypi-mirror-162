from __future__ import annotations
from dataclasses import dataclass
from abc import ABC, abstractmethod
from .expr import Expr
from owl.owl_token import Token
from typing import List, Optional


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor):
        pass


@dataclass
class BlockStmt(Stmt):
    statements: List[Stmt]

    def accept(self, visitor: Visitor):
        return visitor.visit_block_stmt(self)


@dataclass
class ExpressionStmt(Stmt):
    expression: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_expression_stmt(self)


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_branch: Stmt
    else_branch: Stmt

    def accept(self, visitor: Visitor):
        return visitor.visit_if_stmt(self)


@dataclass
class PrintStmt(Stmt):
    expression: Expr

    def accept(self, visitor: Visitor):
        return visitor.visit_print_stmt(self)


@dataclass
class ReturnStmt(Stmt):
    keyword: Token
    value: Optional[Expr]

    def accept(self, visitor: Visitor):
        return visitor.visit_return_stmt(self)


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor: Visitor):
        return visitor.visit_while_stmt(self)


@dataclass
class VarDeclaration(Stmt):
    name: Token
    initializer: Optional[Expr]

    def accept(self, visitor: Visitor):
        return visitor.visit_var_declaration(self)


@dataclass
class FunctionDeclaration(Stmt):
    name: Token
    parameters: List[Token]
    body: List[Stmt]

    def accept(self, visitor: Visitor):
        return visitor.visit_function_declaration(self)


class Visitor(ABC):
    @abstractmethod
    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        pass

    @abstractmethod
    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        pass

    @abstractmethod
    def visit_if_stmt(self, stmt: IfStmt) -> None:
        pass

    @abstractmethod
    def visit_print_stmt(self, stmt: PrintStmt) -> None:
        pass

    @abstractmethod
    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        pass

    @abstractmethod
    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        pass

    @abstractmethod
    def visit_var_declaration(self, stmt: VarDeclaration) -> None:
        pass

    @abstractmethod
    def visit_function_declaration(self, stmt: FunctionDeclaration) -> None:
        pass
