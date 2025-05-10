import inspect
from monkey_token.token import *
from util.timer import Timer
from lexer.lexer import get_lexer, Lexer

timer = Timer()

def check(tokens:[], lexer: Lexer):
    for i, expected_token in enumerate(tokens):
        actual_token = lexer.next_token()
        if actual_token.token_type != expected_token.token_type:
            raise Exception(f'Wrong token_type expected:[{i}]={expected_token.token_type} got:[{actual_token.token_type}]')
        if actual_token.literal != expected_token.literal:
            raise Exception(f'Wrong val expected:[{i}]={expected_token.literal} got:[{actual_token.literal}]')


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
    check(tokens, lexer)

    print(f'Run {func_name} ok!\tTake: {timer.elapse()}')


def test_next_token_02():
    timer.start()
    func_name = inspect.currentframe().f_code.co_name
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
              Token(SEMICOLON, ';'),
              Token(RBRACE, '}'),
              Token(SEMICOLON, ';'),
              Token(LET, 'let'),
              Token(IDENT, 'result'),
              Token(ASSIGN, '='),
              Token(IDENT, 'add'),
              Token(LPAREN, '('),
              Token(IDENT, 'five'),
              Token(COMMA, ','),
              Token(IDENT, 'ten'),
              Token(RPAREN, ')'),
              Token(SEMICOLON, ';'),
              Token(EOF, NULL),
              ]

    lexer = get_lexer(code)
    check(tokens, lexer)
    print(f'Run {func_name} ok!\tTake: {timer.elapse()}')


def test_next_token_03():
    timer.start()
    func_name = inspect.currentframe().f_code.co_name
    code = """
        let five = 5;
        let ten = 10;
let add = fn(x, y) {
x + y;
};

let result = add(five, ten);
!-/*5;
5 < 10 > 5;

if (5 < 10) {
  return true;
} else {
  return false;
}

10 == 10;
10 != 9;
    """
    tokens = [Token(LET, "let"),
    Token(IDENT, "five"),
    Token(ASSIGN, "="),
    Token(INT, "5"),
    Token(SEMICOLON, ";"),
    Token(LET, "let"),
    Token(IDENT, "ten"),
    Token(ASSIGN, "="),
    Token(INT, "10"),
    Token(SEMICOLON, ";"),
    Token(LET, "let"),
    Token(IDENT, "add"),
    Token(ASSIGN, "="),
    Token(FUNCTION, "fn"),
    Token(LPAREN, "("),
    Token(IDENT, "x"),
    Token(COMMA, ","),
    Token(IDENT, "y"),
    Token(RPAREN, ")"),
    Token(LBRACE, "{"),
    Token(IDENT, "x"),
    Token(PLUS, "+"),
    Token(IDENT, "y"),
    Token(SEMICOLON, ";"),
    Token(RBRACE, "}"),
    Token(SEMICOLON, ";"),
    Token(LET, "let"),
    Token(IDENT, "result"),
    Token(ASSIGN, "="),
    Token(IDENT, "add"),
    Token(LPAREN, "("),
    Token(IDENT, "five"),
    Token(COMMA, ","),
    Token(IDENT, "ten"),
    Token(RPAREN, ")"),
    Token(SEMICOLON, ";"),
    Token(BANG, "!"),
    Token(MINUS, "-"),
    Token(SLASH, "/"),
    Token(ASTERISK, "*"),
    Token(INT, "5"),
    Token(SEMICOLON, ";"),
    Token(INT, "5"),
    Token(LT, "<"),
    Token(INT, "10"),
    Token(GT, ">"),
    Token(INT, "5"),
    Token(SEMICOLON, ";"),
    Token(IF, "if"),
    Token(LPAREN, "("),
    Token(INT, "5"),
    Token(LT, "<"),
    Token(INT, "10"),
    Token(RPAREN, ")"),
    Token(LBRACE, "{"),
    Token(RETURN, "return"),
    Token(TRUE, "true"),
    Token(SEMICOLON, ";"),
    Token(RBRACE, "}"),
    Token(ELSE, "else"),
    Token(LBRACE, "{"),
    Token(RETURN, "return"),
    Token(FALSE, "false"),
    Token(SEMICOLON, ";"),
    Token(RBRACE, "}"),
    Token(INT, "10"),
    Token(EQ, "=="),
    Token(INT, "10"),
    Token(SEMICOLON, ";"),
    Token(INT, "10"),
    Token(NOT_EQ, "!="),
    Token(INT, "9"),
    Token(SEMICOLON, ";"),
    Token(EOF, NULL)]
    check(tokens, lexer=get_lexer(code))
    print(f'Run {func_name} ok!\tTake: {timer.elapse()}')

if __name__ == '__main__':
    test_next_token_01()
    test_next_token_02()
    test_next_token_03()
