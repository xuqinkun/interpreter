from chapter1.tok import *


class Lexer:
    def __init__(self, code: str, curr=-1, _next=0, peek=''):
        self._code = code
        self._curr = curr
        self._next = _next
        self._peek = peek

    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        if not isinstance(code, str):
            raise ValueError("text must be a string")
        self._code = code

    @property
    def curr(self):
        """当前读"""
        return self._curr

    @curr.setter
    def curr(self, curr):
        if not isinstance(curr, int):
            raise ValueError("curr must be a int")
        self._curr = curr

    @property
    def next(self):
        """向前看一个字符"""
        return self._next

    @next.setter
    def next(self, _next):
        if not isinstance(_next, int):
            raise ValueError("next must be a int")
        self._next = _next

    @property
    def peek(self):
        """当前正在查看的字符"""
        return self._peek

    @peek.setter
    def peek(self, peek):
        self._peek = peek

    def __str__(self):
        return f"Lexer(curr={self.curr}, next={self.next}, peek='{self.peek}')"

    def read_char(self):
        """读入下一个字符，并更新指针位置，如果超出文本长度，将peek置为"""
        if self.next >= len(self.code):
            self.peek = NULL
        else:
            self.peek = self.code[self.next]
        self.curr = self.next
        self.next += 1

    def next_token(self):
        self.skip_whitespace()
        ch = self.peek
        if ch == '=':
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
        elif ch == '{':
            tok = Token(LBRACE, ch)
        elif ch == '}':
            tok = Token(RBRACE, ch)
        elif ch == NULL:
            tok = Token(EOF, ch)
        else:
            if is_letter(self.peek):
                ident = self.read_ident()
                return Token(lookup_ident(ident), ident)
            elif is_digit(self.peek):
                return Token(INT, self.read_number())
            else:
                tok = Token(ILLEGAL, ch)
        self.read_char()
        return tok

    def read_ident(self):
        start = self.curr
        while is_letter(self.peek):
            self.read_char()
        return self.code[start: self.curr]

    def read_number(self):
        start = self.curr
        while is_digit(self.peek):
            self.read_char()

        return self.code[start: self.curr]

    def skip_whitespace(self):
        while self.peek in ['\t', ' ', '\n']:
            self.read_char()


def get_lexer(code: str):
    lexer = Lexer(code)
    lexer.read_char()
    return lexer


def is_letter(ch: str):
    return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z' or ch == '_'


def is_digit(ch: str):
    return '0' <= ch <= '9'
