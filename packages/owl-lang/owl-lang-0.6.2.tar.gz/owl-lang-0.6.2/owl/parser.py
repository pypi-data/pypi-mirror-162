from typing import List, Optional

from .owl_ast.stmt import (
    Stmt,
    PrintStmt,
    ExpressionStmt,
    VarDeclaration,
    BlockStmt,
    IfStmt,
    WhileStmt,
    FunctionDeclaration,
    ReturnStmt,
)
from .owl_ast.expr import (
    Expr,
    Literal,
    Grouping,
    Binary,
    Visitor,
    Unary,
    Variable,
    Assignment,
    Logical,
    FunctionCall,
    Ternary,
)
from .token_type import TokenType
from .owl_token import Token
from .owl_error import ParseError


class Parser:
    tokens: List[Token]
    current: int
    parse_errors: List[ParseError]

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.current = 0
        self.parse_errors = []

    def parse(self) -> List[Stmt]:
        statements = []
        while not self.is_at_end():
            statements.append(self.declaration())
        return statements

    def declaration(self) -> Optional[Stmt]:
        try:
            if self.match(TokenType.VAR):
                return self.variable_declaration()
            if self.match(TokenType.FUN):
                return self.function_declaration("function")
            return self.statement()
        except ParseError as parse_error:
            self.parse_errors.append(parse_error)
            self.synchronize()
            return None

    def variable_declaration(self) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, "Expect variable name.")
        initializer: Optional[Expr] = None
        if self.match(TokenType.EQUAL):
            initializer = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarDeclaration(name, initializer)

    def function_declaration(self, kind: str) -> Stmt:
        name = self.consume(TokenType.IDENTIFIER, f"Expect {kind} name.")
        self.consume(TokenType.LEFT_PAREN, f"Expect '(' after {kind} name.")
        # parse function parameters
        parameters = []
        if not self.check(TokenType.RIGHT_PAREN):
            param = self.consume(TokenType.IDENTIFIER, "Expect parameter name")
            parameters.append(param)

            while self.match(TokenType.COMMA):
                param = self.consume(TokenType.IDENTIFIER, "Expect parameter name")
                parameters.append(param)
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self.consume(TokenType.LEFT_BRACE, f"Expect '{{' before {kind} body.")
        body = self.block_statement()
        return FunctionDeclaration(name, parameters, body)

    def statement(self) -> Stmt:
        if self.match(TokenType.PRINT):
            return self.print_statement()
        if self.match(TokenType.LEFT_BRACE):
            statements = self.block_statement()
            return BlockStmt(statements)
        if self.match(TokenType.IF):
            return self.if_statement()
        if self.match(TokenType.WHILE):
            return self.while_statement()
        if self.match(TokenType.FOR):
            return self.for_statement()
        if self.match(TokenType.RETURN):
            return self.return_statement()
        return self.expression_statement()

    def return_statement(self) -> Stmt:
        keyword = self.previous()
        value = None
        if not self.check(TokenType.SEMICOLON):
            value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after return value.")
        return ReturnStmt(keyword, value)

    def for_statement(self) -> Stmt:
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'.")
        # Parse initializer
        initializer = None
        if self.match(TokenType.SEMICOLON):
            initializer = None
        elif self.match(TokenType.VAR):
            initializer = self.variable_declaration()
        else:
            initializer = self.expression_statement()
        # Parse condition
        condition = None
        if not self.check(TokenType.SEMICOLON):
            condition = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after loop condition.")
        # Parse increment
        increment = None
        if not self.check(TokenType.RIGHT_PAREN):
            increment = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses.")
        # Parse for body
        body = self.statement()
        # desugaring for loop
        if increment is not None:
            body = BlockStmt([body, ExpressionStmt(increment)])
        if condition is None:
            condition = Literal(True)
        body = WhileStmt(condition, body)
        if initializer is not None:
            body = BlockStmt([initializer, body])
        return body

    def while_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")
        body = self.statement()
        return WhileStmt(condition, body)

    def if_statement(self):
        self.consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self.expression()
        self.consume(TokenType.RIGHT_PAREN, "Expect ')' after if condition.")
        then_branch = self.statement()
        else_branch = None
        if self.match(TokenType.ELSE):
            else_branch = self.statement()
        return IfStmt(condition, then_branch, else_branch)

    def block_statement(self) -> List[Stmt]:
        statements = []
        while not self.check(TokenType.RIGHT_BRACE) and not self.is_at_end():
            stmt = self.declaration()
            statements.append(stmt)
        self.consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")
        return statements

    def print_statement(self) -> Stmt:
        value = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(value)

    def expression_statement(self) -> Stmt:
        expr = self.expression()
        self.consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(expr)

    def expression(self) -> Expr:
        return self.assignment()

    def assignment(self) -> Expr:
        expr = self.ternary()
        if self.match(TokenType.EQUAL):
            equal_token = self.previous()
            value = self.assignment()
            if isinstance(expr, Variable):
                name: Token = expr.name
                return Assignment(name, value)

            self.error(equal_token, "Invalid assignment target.")
        return expr

    def ternary(self) -> Expr:
        expr = self.logical_or()
        if self.match(TokenType.QUESTION):
            then_expr = self.ternary()
            self.consume(TokenType.COLON, "Expect ':' after ternary then condition")
            else_expr = self.ternary()
            expr = Ternary(condition=expr, thenExpr=then_expr, elseExpr=else_expr)
        return expr

    def logical_or(self) -> Expr:
        expr = self.logical_and()
        while self.match(TokenType.OR):
            operator = self.previous()
            right = self.logical_and()
            # logical or expression
            expr = Logical(expr, operator, right)
        return expr

    def logical_and(self) -> Expr:
        expr = self.equality()
        while self.match(TokenType.AND):
            operator = self.previous()
            right = self.equality()
            # logical and expression
            expr = Logical(expr, operator, right)
        return expr

    def equality(self) -> Expr:
        expr = self.comparison()
        while self.match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self.previous()
            right = self.comparison()
            expr = Binary(expr, operator, right)
        return expr

    def comparison(self) -> Expr:
        expr = self.term()
        while self.match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self.previous()
            right = self.term()
            expr = Binary(expr, operator, right)
        return expr

    def term(self) -> Expr:
        expr = self.factor()
        while self.match(TokenType.MINUS, TokenType.PLUS):
            operator = self.previous()
            right = self.factor()
            expr = Binary(expr, operator, right)
        return expr

    def factor(self) -> Expr:
        expr = self.unary()
        while self.match(TokenType.SLASH, TokenType.STAR):
            operator = self.previous()
            right = self.unary()
            expr = Binary(expr, operator, right)
        return expr

    def unary(self) -> Expr:
        if self.match(TokenType.BANG, TokenType.MINUS):
            operator = self.previous()
            right = self.unary()
            return Unary(operator, right)
        return self.function_call()

    def function_call(self):
        expr = self.primary()
        while True:
            if self.match(TokenType.LEFT_PAREN):
                expr = self.finish_call(expr)
            else:
                break
        return expr

    def finish_call(self, callee: Expr) -> Expr:
        arguments = []
        if not self.check(TokenType.RIGHT_PAREN):
            argument = self.expression()
            arguments.append(argument)
            while self.match(TokenType.COMMA):
                argument = self.expression()
                arguments.append(argument)

        paren = self.consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")
        return FunctionCall(callee, paren, arguments)

    def primary(self) -> Expr:
        if self.match(TokenType.FALSE):
            return Literal(value=False)
        if self.match(TokenType.TRUE):
            return Literal(value=True)
        if self.match(TokenType.NIL):
            return Literal(value=None)
        if self.match(TokenType.NUMBER, TokenType.STRING):
            token = self.previous()
            return Literal(value=token.literal)

        if self.match(TokenType.IDENTIFIER):
            name = self.previous()
            return Variable(name)

        if self.match(TokenType.LEFT_PAREN):
            expr = self.expression()
            self.consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return Grouping(expr)
        raise self.error(self.peek(), "Expect expression.")

    def consume(self, token_type: TokenType, message: str) -> Token:
        if self.check(token_type):
            return self.advance()
        raise self.error(self.peek(), message)

    def error(self, token: Token, message: str) -> ParseError:
        error = ParseError(token, message)
        return error

    def synchronize(self):
        """
        Discard tokens until we reach the beginning of the next token
        :return:
        """
        # self.advance()
        while not self.is_at_end():
            # end expression statement
            if self.previous().type == TokenType.SEMICOLON:
                return
            keywords = [
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ]
            if self.peek().type in keywords:
                return
            # otherwise advance
            self.advance()

    def match(self, *token_types: TokenType):
        for type in token_types:
            if self.check(type):
                self.advance()
                return True

        return False

    def check(self, type: TokenType) -> bool:
        if self.is_at_end():
            return False

        return self.peek().type == type

    def advance(self) -> Token:
        if not self.is_at_end():
            self.current += 1
        return self.previous()

    def is_at_end(self) -> bool:
        return self.tokens[self.current].type == TokenType.EOF

    def peek(self) -> Token:
        return self.tokens[self.current]

    def previous(self) -> Token:
        return self.tokens[self.current - 1]
