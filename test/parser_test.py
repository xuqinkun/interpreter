from monkey_ast.ast import *
from lexer import lexer
from monkey_parser.parser import Parser

def check_parser_errors(p: Parser):
    errors = p.errors
    if not errors:
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
    return expected_type.copy(obj)

def parse(code):
    l = lexer.get_lexer(code)
    p = Parser.get_parser(l)
    program = p.parse_program()
    check_parser_errors(p)
    return program

def test_let_statements():
    code = """
    let x = 5;let y = 10;
    let foobar = 838 383;
    """
    program = parse(code)
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
    program = parse(code)
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
    program = parse(code)
    check_len(1, len(program.statements))
    stmt = program.statements[0]
    exp = check_type(ExpressionStatement, stmt)
    ident = check_type(Identifier, exp.expression)
    if ident.value != 'foobar':
        raise Exception(f'ident.value is not foobar, got {ident.value}')
    if ident.literal() != 'foobar':
        raise Exception(f'ident.literal is not foobar, got {ident.literal()}')
    return True


def test_integer_literal_expression():
    code = "51;"
    program = parse(code)
    check_len(1, len(program.statements))
    stmt = program.statements[0]
    exp = check_type(ExpressionStatement, stmt)
    literal = check_type(IntegerLiteral, exp.expression)
    if literal.value != 51:
        raise Exception(f"literal.value expected: {51}, got: {literal.value}")
    if literal.literal() != "51":
        raise Exception(f"literal.literal expected: '51', got: '{literal.literal()}'")
    return True

def test_parsing_prefix_expressions():
    codes = [("!5;", "!", 5), ("-15;", "-", 15)]
    for code in codes:
        program = parse(code[0])
        check_len(1, len(program.statements))
        stmt = check_type(ExpressionStatement, program.statements[0])
        exp = check_type(PrefixExpression, stmt.expression)
        if exp.operator != code[1]:
            raise Exception(f"exp.operator is not '{code[1]}'. got {exp.operator}")
        if not test_integer_literal(exp.right, code[2]):
            return False
    return True

def test_integer_literal(exp: Expression, value: int):
    intl = check_type(IntegerLiteral, exp)
    if intl.value != value:
        print(f'intl.value not {value}. got {intl.value}')
        return False
    if intl.literal() != f'{value}':
        print(f'intl.literal not {value}. got {intl.literal()}')
        return False
    return True

def test_parsing_infix_expressions():
    codes = [
        ("5 + 5;", 5, "+", 5),
        ("5 - 5;", 5, "-", 5),
        ("5 * 5;", 5, "*", 5),
        ("5 / 5;", 5, "/", 5),
        ("5 > 5;", 5, ">", 5),
        ("5 < 5;", 5, "<", 5),
        ("5 == 5;", 5, "==", 5),
        ("5 != 5;", 5, "!=", 5),
        ("true == true;", True, "==", True),
        ("true != false;", True, "!=", False),
        ("false == false;", False, "==", False),
    ]
    for code in  codes:
        program = parse(code[0])
        check_len(1, len(program.statements))
        statement = program.statements[0]
        check_type(ExpressionStatement, statement)
        stmt = ExpressionStatement.copy(statement)
        check_type(InfixExpression, stmt.expression)
        exp = InfixExpression.copy(exp=stmt.expression)
        test_infix_expression(exp, code[1], code[2], code[3])
    return True

def test_operator_precedence_parsing():
    codes = [
        (
            "-a * b",
            "((-a) * b)",
        ),
        (
            "!-a",
            "(!(-a))",
        ),
        (
            "a + b + c",
            "((a + b) + c)",
        ),
        (
            "a + b - c",
            "((a + b) - c)",
        ),
        (
            "a * b * c",
            "((a * b) * c)",
        ),
        (
            "a * b / c",
            "((a * b) / c)",
        ),
        (
            "a + b / c",
            "(a + (b / c))",
        ),
        (
            "a + b * c + d / e - f",
            "(((a + (b * c)) + (d / e)) - f)",
        ),
        (
            "3 + 4; -5 * 5",
            "(3 + 4)((-5) * 5)",
        ),
        (
            "5 > 4 == 3 < 4",
            "((5 > 4) == (3 < 4))",
        ),
        (
            "5 < 4 != 3 > 4",
            "((5 < 4) != (3 > 4))",
        ),
        (
            "3 + 4 * 5 == 3 * 1 + 4 * 5",
            "((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))",
        ),
        (
            "true",
            "true",
        ),
        (
            "false",
            "false",
        ),
        (
            "3 > 5 == false",
            "((3 > 5) == false)",
        ),
        (
            "3 < 5 == true",
            "((3 < 5) == true)",
        ),
        (
            "1 + (2 + 3) + 4",
            "((1 + (2 + 3)) + 4)",
        ),
        (
            "(5 + 5) * 2",
            "((5 + 5) * 2)",
        ),
        (
            "2 / (5 + 5)",
            "(2 / (5 + 5))",
        ),
        (
            "-(5 + 5)",
            "(-(5 + 5))",
        ),
        (
            "!(true == true)",
            "(!(true == true))",
        ),
    ]
    for code in codes:
        program = parse(code[0])
        actual = program.string()
        if actual != code[1]:
            print(f"expected: {code[1]} got: {actual}")


def test_identifier(exp: Expression, value: str):
    ident = check_type(Identifier, exp)
    if ident.value != value:
        print(f'ident.value not {value}. got {ident.value}')
        return False
    if ident.literal() != value:
        print(f'ident.literal not {value}. got {ident.literal()}')
        return False
    return True


def test_literal_expression(exp: Expression, expected: object):
    expected_type = type(expected)
    if expected_type == int:
        return test_integer_literal(exp, int(str(expected)))
    elif expected_type == str:
        return test_identifier(exp, str(expected))
    elif expected_type == bool:
        return test_boolean_expression(exp, bool(expected))
    print(f'type of exp not handled. got{expected_type}')
    return False

def test_infix_expression(exp: Expression, left: object,
                          operator: str, right: object):
    op_exp = check_type(InfixExpression, exp)
    if not test_literal_expression(op_exp.left, left):
        return False
    if op_exp.operator != operator:
        print(f"exp.operator is not '{operator}'. got: {op_exp.operator}")
        return False
    if not test_literal_expression(op_exp.right, right):
        return False
    return True


def test_boolean_expression(exp: Expression, value: bool):
    check_type(Boolean, exp)
    if exp.value != value:
        print(f'exp.value not {value} got {exp.value}')
        return False
    if exp.literal() != str(value).lower():
        print(f"literal not {value} got: {exp.literal()}")
        return False
    return True

def test_if_expression():
    code = "if (x < y) {x}"
    program = parse(code)
    check_len(1, len(program.statements))
    stmt = check_type(ExpressionStatement, program.statements[0])
    exp = check_type(IFExpression, stmt.expression)
    if not test_infix_expression(exp.condition, "x", "<", "y"):
        return False
    statements = exp.consequence.statements
    check_len(1, len(statements))
    consequence = check_type(ExpressionStatement, statements[0])
    if not test_identifier(consequence.expression, "x"):
        return False
    if exp.alternative is not None:
        raise Exception(f"exp.alternative statements was not none. got{exp.alternative}")
    return True


def test_if_else_expression():
    code = "if (x < y) {x} else {y}"
    program = parse(code)
    check_len(1, len(program.statements))

    stmt = check_type(ExpressionStatement, program.statements[0])

    exp = check_type(IFExpression, stmt.expression)
    if not test_infix_expression(exp.condition, "x", "<", "y"):
        return False
    statements = exp.consequence.statements
    check_len(1, len(statements))

    consequence = check_type(ExpressionStatement, statements[0])
    if not test_identifier(consequence.expression, "x"):
        return False
    alternative = exp.alternative
    check_len(1, len(alternative.statements))

    alter = check_type(ExpressionStatement, alternative.statements[0])
    if not test_identifier(alter.expression, "y"):
        return False
    return True


def test_function_literal_parsing():
    code = 'fn(x, y) { x + y;}'
    program = parse(code)
    check_len(1, len(program.statements))

    stmt = check_type(ExpressionStatement, program.statements[0])

    func = check_type(FunctionLiteral, stmt.expression)
    check_len(2, len(func.parameters))
    test_literal_expression(func.parameters[0], "x")
    test_literal_expression(func.parameters[1], "y")
    check_len(1, len(func.body.statements))

    body_stmt = check_type(ExpressionStatement, func.body.statements[0])
    if not test_infix_expression(body_stmt.expression, "x", "+", "y"):
        return False
    return True


def test_function_parameter_parsing():
    codes = [
        ("fn() {};", []),
        ("fn(x) {};", ["x"]),
        ("fn(x, y, z) {};", ["x", "y", "z"]),
    ]
    for code in codes:
        program = parse(code[0])
        stmt = check_type(ExpressionStatement, program.statements[0])
        func = check_type(FunctionLiteral, stmt.expression)
        check_len(len(code[1]), len(func.parameters))
        for param, ident in zip(func.parameters, code[1]):
            if not test_literal_expression(param, ident):
                return False
    return True

if __name__ == '__main__':
    if test_let_statements():
        print('test_let_statements passed!')
    if test_return_statement():
        print('test_return_statement passed!')
    if test_identifier_expression():
        print('test_identifier_expression passed!')
    if test_integer_literal_expression():
        print('test_integer_literal_expression passed!')
    if test_parsing_prefix_expressions():
        print('test_parsing_prefix_expressions passed!')
    if test_parsing_infix_expressions():
        print('test_parsing_infix_expressions passed!')
    if test_operator_precedence_parsing():
        print('test_operator_precedence_parsing passed!')
    if test_if_expression():
        print('test_if_expression passed!')
    if test_if_else_expression():
        print('test_if_else_expression passed!')
    if test_function_literal_parsing():
        print('test_function_literal_parsing passed!')
    if test_function_parameter_parsing():
        print('test_function_parameter_parsing passed!')