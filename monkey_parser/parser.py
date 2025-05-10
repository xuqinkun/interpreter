from typing import Optional,Dict,Callable
from enum import Enum
from lexer.lexer import Lexer
from monkey_ast.ast import (
    Program,
    Statement,
    LetStatement,
    ReturnStatement,
    ExpressionStatement,
    Identifier,
    Expression,
    IntegerLiteral,
    PrefixExpression,
)
from monkey_token.token import *
from dataclasses import dataclass

class Priority(Enum):
    BLANK = 0
    LOWEST = 1
    EQUALS = 2       # ==
    LESS_GREATER = 3 # > or <
    SUM = 4          # +
    PRODUCT = 5      # *
    PREFIX = 6       # -X or !X
    CALL = 7         # func(X)


@dataclass
class Parser:
    # 定义函数类型别名
    PrefixParseFn = Callable[[], Expression]
    InfixParseFn = Callable[[Expression], Expression]

    lexer: Lexer
    line: int=0
    errors: list[str]=None
    curr: Token=''
    peek: Token=''
    prefix_parse_fns: Dict[str, PrefixParseFn] = None
    infix_parse_fns: Dict[str, InfixParseFn] = None

    def next_token(self):
        self.curr = self.peek
        self.peek = self.lexer.next_token()

    def parse_program(self)->Program:
        statements = []
        program = Program(statements)
        while self.curr.token_type != EOF:
            stmt = self.parse_statement()
            if stmt is not None:
                statements.append(stmt)
            self.next_token()
        return program

    def parse_statement(self)->Optional[Statement]:
        if self.curr.token_type == LET:
            return self.parse_let_statement()
        elif self.curr.token_type == RETURN:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()

    def parse_let_statement(self)->Optional[LetStatement]:
        stmt = LetStatement(self.curr)
        if not self.expect_peek(IDENT):
            return None
        stmt.name = Identifier(self.curr, self.curr.literal)
        if not self.expect_peek(ASSIGN):
            return None
        # 跳过对表达式的处理，直到遇见分号
        while not self.curr_token_is(SEMICOLON):
            self.next_token()
        return stmt

    def parse_return_statement(self):
        stmt = ReturnStatement(self.curr)
        self.next_token()
        while not self.curr_token_is(SEMICOLON):
            self.next_token()
        return stmt

    def parse_expression_statement(self):
        stmt = ExpressionStatement(token=self.curr)
        stmt.expression = self.parse_expression(Priority.LOWEST)
        if self.peek_token_is(SEMICOLON):
            self.next_token()
        return stmt

    def parse_expression(self, priority):
        token_type = self.curr.token_type
        prefix = self.prefix_parse_fns.get(token_type, None)
        if prefix is None:
            err_msg = f"no prefix parse function for '{token_type}' found"
            self.append_error(err_msg)
            return None
        return prefix()

    def append_error(self, err_msg: str):
        if self.errors is None:
            self.errors = []
        self.errors.append(err_msg)


    def peek_error(self, token_type):
        err_msg = f"line:{self.lexer.lino}: expected next token to be {token_type}, got {self.peek.token_type} instead"
        self.append_error(err_msg)

    def curr_token_is(self, token_type: str):
        return self.curr.token_type == token_type

    def peek_token_is(self, token_type: str):
        return self.peek.token_type == token_type

    def expect_peek(self, token_type: str):
        if self.peek_token_is(token_type):
            self.next_token()
            return True
        else:
            self.peek_error(token_type)
            return False

    def register_prefix(self, token_type: str, fn: PrefixParseFn):
        """注册前缀解析函数"""
        self.prefix_parse_fns[token_type] = fn

    def register_infix(self, token_type: str, fn: InfixParseFn):
        """注册中缀解析函数"""
        self.infix_parse_fns[token_type] = fn

    def parse_identifier(self) -> Optional[Expression]:
        return Identifier(token=self.curr, value=self.curr.literal)

    def parse_integer_literal(self) -> Optional[Expression]:
        lit = IntegerLiteral(token=self.curr)
        literal = lit.literal()
        if not literal.isdigit():
            self.append_error(f'Could not parse {literal} as integer')
            return None
        lit.value = int(literal)
        return lit

    def parse_prefix_expression(self):
        exp = PrefixExpression(token=self.curr, operator=self.curr.literal)
        self.next_token()
        exp.right = self.parse_expression(Priority.PREFIX)
        return exp

    @staticmethod
    def get_parser(lex: Lexer):
        p = Parser(lex)
        p.errors = []
        p.prefix_parse_fns = {}
        p.register_prefix(IDENT, p.parse_identifier)
        p.register_prefix(INT, p.parse_integer_literal)
        p.register_prefix(BANG, p.parse_prefix_expression)
        p.register_prefix(MINUS, p.parse_prefix_expression)
        p.next_token()
        p.next_token()
        return p