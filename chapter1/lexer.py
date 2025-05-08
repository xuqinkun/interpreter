from chapter1.tok import *

class Lexer:
    def __init__(self, text: str, curr: int=0, next: int=0, peek: str=''):
        self.text = text
        self.curr = curr
        self.next = next
        self.peek = peek

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if not isinstance(text, str):
            raise ValueError("text must be a string")
        self._text = text

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

    def read(self):
        """读入下一个字符，并更新指针位置，如果超出文本长度，将peek置为"""
        if self.next >= len(self.text):
            self.peek = EOF
        else:
            self.peek = self.text[self.next]
        self.curr = self.next
        self.next += 1

    def next_token(self):
        self.read()
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
        elif ch == EOF:
            tok = Token(EOF, ch)
        else:
            tok = Token(ILLEGAL, ch)
        return tok

def get_lexer(text: str):
    lexer = Lexer(text)
    return lexer