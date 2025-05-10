from typing import Optional

from lexer.lexer import Lexer
from monkey_ast.ast import (
    Program,
    Statement,
    LetStatement,
    Identifier
)
from monkey_token.token import *
from dataclasses import dataclass


@dataclass
class Parser:
    lexer: Lexer
    curr: Token=''
    peek: Token=''

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
        return None

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

    def curr_token_is(self, token_type: str):
        return self.curr.token_type == token_type

    def peek_token_is(self, token_type: str):
        return self.peek.token_type == token_type

    def expect_peek(self, token_type: str):
        if self.peek_token_is(token_type):
            self.next_token()
            return True
        else:
            return False


def get_parser(lex: Lexer):
    p = Parser(lex)
    p.next_token()
    p.next_token()
    return p