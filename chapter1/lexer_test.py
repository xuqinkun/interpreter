import inspect
from chapter1.tok import *
from util.timer import Timer
from chapter1.lexer import get_lexer

timer = Timer()

def test_next_token_01():
    timer.start()
    func_name = inspect.currentframe().f_code.co_name
    code = '=+(){},;'
    tokens = [Token(ASSIGN, '='),
              Token(PLUS, '+'),
              Token(LPAREN, '('),
              Token(RPAREN, ')'),
              Token(LBRACE, '{'),
              Token(RBRACE, '}'),
              Token(COMMA, ','),
              Token(SEMICOLON, ';'),
              Token(EOF, NULL),
              ]

    lexer = get_lexer(code)
    for expected_token in tokens:
        actual_token = lexer.next_token()
        if actual_token.token_type != expected_token.token_type:
            print(f'Wrong token_type expected:[{expected_token.token_type}] got:[{actual_token.token_type}]')
        if actual_token.val != expected_token.val:
            print(f'Wrong val expected:[{expected_token.val}] got:[{actual_token.val}]')

    print(f'Run {func_name} ok!\tTake: {timer.elapse()}')


def test_next_token_02():
    code = """
    let five = 5;
    let ten = 10;
    let add = fn(x,y) {
        x+y;
    };
    let result = add(five, ten);
    """
    tokens = [Token(LET, 'let'),
              Token(IDENT, 'five'),
              Token(ASSIGN, '='),
              Token(INT, '5'),
              Token(SEMICOLON, ';'),
              Token(LET, 'let'),
              Token(IDENT, 'ten'),
              Token(ASSIGN, '='),
              Token(INT, '10'),
              Token(SEMICOLON, ';'),
              Token(LET, 'let'),
              Token(IDENT, 'add'),
              Token(ASSIGN, '='),
              Token(FUNCTION, 'fn'),
              Token(LPAREN, '('),
              Token(IDENT, 'x'),
              Token(COMMA, ','),
              Token(IDENT, 'y'),
              Token(RPAREN, ')'),
              Token(LBRACE, '{'),
              Token(IDENT, 'x'),
              Token(PLUS, '+'),
              Token(IDENT, 'y'),
              Token(RBRACE, '}'),
              Token(SEMICOLON, ';'),
              Token(LET, 'let'),
              Token(IDENT, 'result'),
              Token(ASSIGN, '='),
              Token(IDENT, 'add'),
              Token(SEMICOLON, ';'),
              Token(LPAREN, '('),
              Token(IDENT, 'five'),
              Token(COMMA, ','),
              Token(IDENT, 'ten'),
              Token(RPAREN, ')'),
              Token(SEMICOLON, ';'),
              Token(EOF, NULL),
              ]

    lexer = get_lexer(code)
    for expected_token in tokens:
        actual_token = lexer.next_token()
        if actual_token.token_type != expected_token.token_type:
            print(f'Wrong token_type expected:[{expected_token.token_type}] got:[{actual_token.token_type}]')
        if actual_token.val != expected_token.val:
            print(f'Wrong val expected:[{expected_token.val}] got:[{actual_token.val}]')
    print('Accepted!')

if __name__ == '__main__':
    test_next_token_02()