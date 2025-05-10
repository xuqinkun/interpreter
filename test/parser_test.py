from monkey_ast.ast import Statement, LetStatement
from lexer import lexer
from monkey_parser.parser import Parser,get_parser

def check_parser_errors(p: Parser):
    errors = p.errors
    if errors is None:
        return False
    print(f'parser has {len(errors)} errors')
    for err in errors:
        print(f'parse error:{err}')
    return True

def test_let_statements():
    l = lexer.get_lexer(code)
    p = get_parser(l)
    program = p.parse_program()
    if check_parser_errors(p):
        print(f'FAILED')
        return False
    if program is None:
        raise Exception("ParseProgram return None")
    n = len(program.statements)
    if n != 3:
        raise Exception(f"Wrong statements number, expected 3 got {n}")
    expected_idents = ["x", "y", "foobar"]
    for i, ident in enumerate(expected_idents):
        stmt = program.statements[i]
        if not check_let_statements(stmt, ident):
            return False
    return True


def check_let_statements(stmt: Statement, name: str):
    if stmt.literal() != "let":
        print(f"Expect let, got {stmt.literal()}")
        return False
    if not isinstance(stmt, LetStatement):
        print(f"stmt not LetStatement, got={type(stmt)}")
        return False
    let_stmt = LetStatement(stmt.token, stmt.name)
    if let_stmt.name.value != name:
        print(f"let_stmt.name.value not {name} got {let_stmt.name.value}")
        return False
    if let_stmt.name.literal() != name:
        print(f"let_stmt.name.literal() not {name} got {let_stmt.name.literal()}")
        return False
    return True


if __name__ == '__main__':
    code = """
        let x  5;let  = 10;
        let  = 838 383;
        """
    if test_let_statements():
        print('All cases accepted!')