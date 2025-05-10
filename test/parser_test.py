from monkey_ast.ast import *
from lexer import lexer
from monkey_parser.parser import Parser

def check_parser_errors(p: Parser):
    errors = p.errors
    if errors is None:
        return False
    print(f'parser has {len(errors)} errors')
    for err in errors:
        print(f'parse error:{err}')
    return True

def check_len(expected_len:int, actual_len:int):
    if expected_len != actual_len:
        raise Exception(f"Wrong statements number, expected {expected_len} got {actual_len}")

def check_type(expected_type: type, obj: object):
    if not isinstance(obj, expected_type):
        raise Exception(f"Wrong type error, expected: {expected_type} actual:{type(obj)}")

def test_let_statements():
    code = """
    let x  5;let  = 10;
    let  = 838 383;
    """
    l = lexer.get_lexer(code)
    p = Parser.get_parser(l)
    program = p.parse_program()
    check_parser_errors(p)
    if program is None:
        raise Exception("ParseProgram return None")
    check_len(3, len(program.statements))
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


def test_return_statement():
    code = """
    return 5;
    return 10;
    return 993 322;
    """
    l = lexer.get_lexer(code)
    p = Parser.get_parser(l)
    program = p.parse_program()
    check_parser_errors(p)
    check_len(3, len(program.statements))
    for stmt in program.statements:
        if not isinstance(stmt, ReturnStatement):
            print(f"stmt not ReturnStatement, got={type(stmt)}")
            continue
        return_stmt = ReturnStatement(stmt.token)
        if return_stmt.literal() != 'return':
            print(f'return_stmt.literal not return, got{return_stmt.literal()}')
    return True

def test_identifier_expression():
    code = 'foobar;'
    l = lexer.get_lexer(code)
    p = Parser.get_parser(l)
    program = p.parse_program()
    check_parser_errors(p)
    check_len(1, len(program.statements))
    stmt = program.statements[0]
    check_type(ExpressionStatement, stmt)
    exp = ExpressionStatement(token=stmt.token, expression=stmt.expression)
    check_type(Identifier, exp.expression)
    ident = Identifier(token=exp.token, value=exp.literal())
    if ident.value != 'foobar':
        raise Exception(f'ident.value is not foobar, got {ident.value}')
    if ident.literal() != 'foobar':
        raise Exception(f'ident.literal is not foobar, got {ident.literal()}')
    return True


def test_integer_literal_expression():
    code = "51;"
    l = lexer.get_lexer(code)
    p = Parser.get_parser(l)
    program = p.parse_program()
    check_parser_errors(p)
    check_len(1, len(program.statements))
    stmt = program.statements[0]
    check_type(ExpressionStatement, stmt)
    exp = ExpressionStatement(token=stmt.token, expression=stmt.expression)
    check_type(IntegerLiteral, exp.expression)
    literal = IntegerLiteral(token=exp.token, value=exp.expression.value)
    if literal.value != 51:
        raise Exception(f"literal.value expected: {51}, got: {literal.value}")
    if literal.literal() != "51":
        raise Exception(f"literal.literal expected: '51', got: '{literal.literal()}'")
    return True

if __name__ == '__main__':
    # if test_let_statements():
    #     print('test_let_statements accepted!')
    if test_return_statement():
        print('test_return_statement accepted!')
    if test_identifier_expression():
        print('test_return_statement accepted!')
    if test_integer_literal_expression():
        print('test_integer_literal_expression accepted!')