from monkey_ast.ast import LetStatement, Identifier, Program
from monkey_token.token import *
from util.test_util import run_cases


def test_string():
    statements = [
        LetStatement(Token(LET, 'let'), Identifier(IDENT, 'var'), Identifier(IDENT, 'anotherVar'))
    ]
    program = Program(statements)
    code = program.string()
    if code != 'let var = anotherVar;':
        return False, f"program.string() wrong. got={code}"
    return True


if __name__ == '__main__':
    run_cases([test_string])
