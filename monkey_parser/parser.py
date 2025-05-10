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
    Expression, IntegerLiteral
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
    PrefixParseFn = Callable[['Parser'], Expression]
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
        prefix = self.prefix_parse_fns[self.curr.token_type]
        if prefix is None:
            return None
        return prefix(self)

    def peek_error(self, token_type):
        if self.errors is None:
            self.errors = []
        err_msg = f"line:{self.lexer.lino}: expected next token to be {token_type}, got {self.peek.token_type} instead"
        self.errors.append(err_msg)

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

    @staticmethod
    def get_parser(lex: Lexer):
        p = Parser(lex)
        p.prefix_parse_fns = {}
        p.register_prefix(IDENT, parse_identifier)
        p.register_prefix(INT, parse_integer_literal)
        p.next_token()
        p.next_token()
        return p

def parse_identifier(p: Parser)->Optional[Expression]:
    return Identifier(token=p.curr, value=p.curr.literal)

def parse_integer_literal(p: Parser)->Expression:
    lit = IntegerLiteral(token=p.curr)
    literal = lit.literal()
    if not literal.isdigit():
        p.errors.append(f'Could not parse {literal} as integer')
        return None
    lit.value = int(literal)
    return lit