class Token:
    def __init__(self, token_type: str='', val: str=''):
        self._token_type = token_type
        self._val = val

    def __str__(self):
        return f"Token(token_type='{self.token_type}', val='{self.val}')"

    @property
    def token_type(self):
        return self._token_type

    @token_type.setter
    def token_type(self, token_type):
        self._token_type = token_type

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, val):
        self._val = val


ILLEGAL = "ILLEGAL"
EOF = "EOF"

# 标识符+字面量
IDENT = "IDENT"
INT = "INT"

# 运算符
ASSIGN = "="
PLUS = "+"

# 分隔符
COMMA = ","
SEMICOLON = ":"

LPAREN = "("
RPAREN = ")"
LBRACE = "{"
RBRACE = "}"

# 关键字
FUNCTION = "FUNCTION"
LET = "LET"

# EOF的值
NULL = '\0'

keywords = {
    'fn': FUNCTION,
    'let': LET
}

def lookup_ident(ident: str):
    return keywords.get(ident, IDENT)