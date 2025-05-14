from monkey_ast.ast import LetStatement, Identifier, Program
from monkey_token.token import *


def test_string():
    statements = [
        LetStatement(Token(LET, 'let'), Identifier(IDENT, 'var'), Identifier(IDENT, 'anotherVar'))
    ]
    program = Program(statements)
    code = program.string()
    if code != 'let var = anotherVar;':
        print(f"program.string() wrong. got={code}")
        return False
    return True


if __name__ == '__main__':
    if test_string():
        print('Passed')
