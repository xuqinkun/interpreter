from chapter1.tok import *
from chapter1.lexer import get_lexer

def test_next_token():
    input = '=+(){},;'
    tokens = [Token(ASSIGN, '='),
              Token(PLUS, '+'),
              Token(LPAREN, '('),
              Token(RPAREN, ')'),
              Token(LBRACE, '{'),
              Token(RBRACE, '}'),
              Token(COMMA, ','),
              Token(SEMICOLON, ';'),
              Token(EOF, ''),
              ]

    lexer = get_lexer(input)
    for token in tokens:
        tok = lexer.next_token()
        if tok.token_type != token.token_type:
            print(f'Wrong token_type expected:[{token.token_type}] got:[{tok.token_type}]')
        if tok.val != token.val:
            print(f'Wrong val expected:[{token.val}] got:[{tok.val}]')
    print('Accepted!')

if __name__ == '__main__':
    test_next_token()