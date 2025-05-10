class Token:
    def __init__(self, token_type: str='', val: str=''):
        self._token_type = token_type
        self._literal = val

    def __repr__(self):
        return f"Token(token_type='{self.token_type}', val='{self.literal}')"

    @property
    def token_type(self):
        return self._token_type

    @token_type.setter
    def token_type(self, token_type):
        self._token_type = token_type

    @property
    def literal(self):
        return self._literal

    @literal.setter
    def literal(self, literal):
        self._literal = literal


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
SEMICOLON = ";"

LPAREN = "("
RPAREN = ")"
LBRACE = "{"
RBRACE = "}"

BANG = "!"
MINUS = "-"
SLASH = "/"
ASTERISK = "*"
LT = "<"
GT = ">"
IF = "if"
RETURN = "return"
TRUE = "true"
ELSE = "else"
FALSE = "false"
EQ = "=="
NOT_EQ = "!="


# 关键字
FUNCTION = "FUNCTION"
LET = "LET"

# EOF的值
NULL = '\0'

keywords = {
    'fn': FUNCTION,
    'let': LET,
    'if': IF,
    'return': RETURN,
    'true':TRUE,
    'false':FALSE,
    'else':ELSE,
}


def lookup_ident(ident: str):
    return keywords.get(ident, IDENT)