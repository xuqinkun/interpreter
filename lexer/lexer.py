from monkey_token.token import *
from dataclasses import dataclass


@dataclass
class Lexer:
    code: str
    ch: str = ''
    curr: int = -1
    next: int = 0
    lino: int = 0

    def __str__(self):
        return f"Lexer(curr={self.curr}, next={self.next}, peek='{self.ch}')"

    def read_char(self):
        """读入下一个字符，并更新指针位置，如果超出文本长度，将peek置为"""
        if self.next >= len(self.code):
            self.ch = NULL
        else:
            self.ch = self.code[self.next]
        self.curr = self.next
        self.next += 1

    def peek(self):
        if self.next >= len(self.code):
            return NULL
        else:
            return self.code[self.next]

    def next_token(self):
        self.skip_whitespace()
        ch = self.ch
        if ch == '=':
            if self.peek() == '=':
                self.read_char()
                tok = Token(EQ, ch + self.ch)
            else:
                tok = Token(ASSIGN, ch)
        elif ch == ';':
            tok = Token(SEMICOLON, ch)
        elif ch == '(':
            tok = Token(LPAREN, ch)
        elif ch == ')':
            tok = Token(RPAREN, ch)
        elif ch == ',':
            tok = Token(COMMA, ch)
        elif ch == '+':
            tok = Token(PLUS, ch)
        elif ch == '-':
            tok = Token(MINUS, ch)
        elif ch == '&':
            if self.peek() == '&':
                self.read_char()
                tok = Token(LOGIC_AND, ch + self.ch)
            else:
                tok = Token(BITWISE_AND, ch)
        elif ch == '|':
            if self.peek() == '|':
                self.read_char()
                tok = Token(LOGIC_OR, ch + self.ch)
            else:
                tok = Token(BITWISE_OR, ch)
        elif ch == '!':
            if self.peek() == '=':
                self.read_char()
                tok = Token(NOT_EQ, ch + self.ch)
            else:
                tok = Token(BANG, ch)
        elif ch == '/':
            tok = Token(SLASH, ch)
        elif ch == '*':
            tok = Token(ASTERISK, ch)
        elif ch == '<':
            tok = Token(LT, ch)
        elif ch == '>':
            tok = Token(GT, ch)
        elif ch == '{':
            tok = Token(LBRACE, ch)
        elif ch == '}':
            tok = Token(RBRACE, ch)
        elif ch == '[':
            tok = Token(LBRACKET, ch)
        elif ch == ']':
            tok = Token(RBRACKET, ch)
        elif ch == '"' or ch == "'":
            tok = Token(STRING, self.read_string())
        elif ch == NULL:
            tok = Token(EOF, ch)
        else:
            if is_letter(self.ch):
                ident = self.read_ident()
                return Token(lookup_ident(ident), ident)
            elif is_digit(self.ch):
                return Token(INT, self.read_number())
            else:
                tok = Token(ILLEGAL, ch)
        self.read_char()
        return tok

    def read_ident(self):
        start = self.curr
        while is_letter(self.ch):
            self.read_char()
        return self.code[start: self.curr]

    def read_number(self):
        start = self.curr
        while is_digit(self.ch):
            self.read_char()
        return self.code[start: self.curr]

    def read_string(self):
        start = self.curr + 1
        while True:
            self.read_char()
            if self.ch == '"' or self.ch == NULL or self.ch == "'":
                break
        return self.code[start: self.curr]

    def skip_whitespace(self):
        while self.ch in ['\t', ' ', '\n']:
            if self.ch == '\n':
                self.lino += 1
            self.read_char()


def get_lexer(code: str):
    lexer = Lexer(code)
    lexer.read_char()
    return lexer


def is_letter(ch: str):
    return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or ch == '_'


def is_digit(ch: str):
    return '0' <= ch <= '9'
