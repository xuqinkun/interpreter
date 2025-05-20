from monkey_lexer import lexer
from monkey_ast.ast import *
from monkey_parser.parser import Parser
from util.test_util import *


def test_let_statements():
    codes = [
        ("let x = 5;", "x", 5),
        ("let y = true;", "y", True),
        ("let foobar = y;", "foobar", "y"),
    ]
    for code in codes:
        program = parse(code[0])
        check_len(1, program.statements)
        stmt = program.statements[0]
        if not test_let_statement(stmt, code[1]):
            return False
        output = check_type(LetStatement, stmt)
        if type(output) == tuple:
            return output
        output = test_literal_expression(output.value, code[2])
        if type(output) == tuple:
            return output
    return True


def test_let_statement(s: Statement, name: str):
    if s.literal() != 'let':
        return False, f's.literal not "let" got {s.literal()}'
    let_stmt = check_type(LetStatement, s)
    if type(let_stmt) == tuple:
        return let_stmt
    if let_stmt.name.value != name:
        return False, f'let_stmt.name.value not "{name}" got {let_stmt.name.value}'
    if let_stmt.name.literal() != name:
        return False, f'let_stmt.name.literal not "{name}" got {let_stmt.name.literal}'
    return True


def check_let_statements(stmt: Statement, name: str):
    if stmt.literal() != "let":
        return False, f"Expect let, got {stmt.literal()}"
    if not isinstance(stmt, LetStatement):
        return False, f"stmt not LetStatement, got={type(stmt)}"
    let_stmt = LetStatement(stmt.token, stmt.name)
    if let_stmt.name.value != name:
        return False, f"let_stmt.name.value not {name} got {let_stmt.name.value}"
    if let_stmt.name.literal() != name:
        return False, f"let_stmt.name.literal() not {name} got {let_stmt.name.literal()}"
    return True


def test_return_statement():
    code = """
    return 5;
    return 10;
    return 993322;
    """
    program = parse(code)
    output = check_len(3, program.statements)
    if type(output) == tuple:
        return output
    for stmt in program.statements:
        if not isinstance(stmt, ReturnStatement):
            return False, f"stmt not ReturnStatement, got={type(stmt)}"
        return_stmt = ReturnStatement(stmt.token)
        if return_stmt.literal() != 'return':
            return False, f'return_stmt.literal not return, got{return_stmt.literal()}'
    return True


def test_identifier_expression():
    code = 'foobar;'
    program = parse(code)
    output = check_len(1, program.statements)
    if type(output) == tuple:
        return output
    stmt = program.statements[0]
    exp = check_type(ExpressionStatement, stmt)
    if type(exp) == tuple:
        return exp
    ident = check_type(Identifier, exp.expression)
    if type(ident) == tuple:
        return ident
    if ident.value != 'foobar':
        return False, f'ident.value is not foobar, got {ident.value}'
    if ident.literal() != 'foobar':
        return False, f'ident.literal is not foobar, got {ident.literal()}'
    return True


def test_integer_literal_expression():
    code = "51;"
    program = parse(code)
    check_len(1, program.statements)
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
        check_len(1, program.statements)
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
        return False, f'intl.value not {value}. got {intl.value}'
    if intl.literal() != f'{value}':
        return False, f'intl.literal not {value}. got {intl.literal()}'
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
    for code in codes:
        program = parse(code[0])
        check_len(1, program.statements)
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
        (
            "a + add(b * c) + d",
            "((a + add((b * c))) + d)",
        ),
        (
            "add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))",
            "add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))",
        ),
        (
            "add(a + b + c * d / f + g)",
            "add((((a + b) + ((c * d) / f)) + g))",
        ),
        (
            "a * [1, 2, 3, 4][b * c] * d",
            "((a * ([1, 2, 3, 4][(b * c)])) * d)",
        ),
        (
            "add(a * b[2], b[1], 2 * [1, 2][1])",
            "add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))",
        ),
    ]
    for code in codes:
        program = parse(code[0])
        actual = program.string()
        if actual != code[1]:
            print(f"expected: {code[1]} got: {actual}")
            return False
    return True


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
    return False, f'type of exp not handled. got{expected_type}'


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
        return False, f'exp.value not {value} got {exp.value}'
    if exp.literal() != str(value).lower():
        return False, f"literal not {value} got: {exp.literal()}"
    return True


def test_if_expression():
    code = "if (x < y) {x}"
    program = parse(code)
    check_len(1, program.statements)
    stmt = check_type(ExpressionStatement, program.statements[0])
    exp = check_type(IFExpression, stmt.expression)
    if not test_infix_expression(exp.condition, "x", "<", "y"):
        return False
    statements = exp.consequence.statements
    check_len(1, statements)
    consequence = check_type(ExpressionStatement, statements[0])
    if not test_identifier(consequence.expression, "x"):
        return False
    if exp.alternative is not None:
        raise Exception(f"exp.alternative statements was not none. got{exp.alternative}")
    return True


def test_if_else_expression():
    code = "if (x < y) {x} else {y}"
    program = parse(code)
    check_len(1, program.statements)

    stmt = check_type(ExpressionStatement, program.statements[0])

    exp = check_type(IFExpression, stmt.expression)
    if not test_infix_expression(exp.condition, "x", "<", "y"):
        return False
    statements = exp.consequence.statements
    check_len(1, statements)

    consequence = check_type(ExpressionStatement, statements[0])
    if not test_identifier(consequence.expression, "x"):
        return False
    alternative = exp.alternative
    check_len(1, alternative.statements)

    alter = check_type(ExpressionStatement, alternative.statements[0])
    if not test_identifier(alter.expression, "y"):
        return False
    return True


def test_function_literal_parsing():
    code = 'fn(x, y) { x + y;}'
    program = parse(code)
    check_len(1, program.statements)

    stmt = check_type(ExpressionStatement, program.statements[0])

    func = check_type(FunctionLiteral, stmt.expression)
    check_len(2, func.parameters)
    test_literal_expression(func.parameters[0], "x")
    test_literal_expression(func.parameters[1], "y")
    check_len(1, func.body.statements)

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
        check_len(len(code[1]), func.parameters)
        for param, ident in zip(func.parameters, code[1]):
            if not test_literal_expression(param, ident):
                return False
    return True


def test_call_expression_parsing():
    code = "add(1, 2*3, 4+5);"
    program = parse(code)
    if not check_len(1, program.statements):
        return False
    stmt = check_type(ExpressionStatement, program.statements[0])
    exp = check_type(CallExpression, stmt.expression)
    if not test_identifier(exp.function, "add"):
        return False
    check_len(3, exp.arguments)
    test_literal_expression(exp.arguments[0], 1)
    test_infix_expression(exp.arguments[1], 2, "*", 3)
    test_infix_expression(exp.arguments[2], 4, "+", 5)
    return True


def test_string_literal_expression():
    code = '"hello world";'
    program = parse(code)
    stmt = check_type(ExpressionStatement, program.statements[0])
    literal = check_type(StringLiteral, stmt.expression)
    if literal.value != 'hello world':
        print(f'literal.value not hello world, got {literal.value}')
        return False
    return True


def test_parsing_array_literals():
    code = "[1, 2 * 2, 3+3]"
    program = parse(code)
    stmt = check_type(ExpressionStatement, program.statements[0])
    array = check_type(ArrayLiteral, stmt.expression)
    check_len(3, array.elements)
    if not test_integer_literal(array.elements[0], 1):
        return False
    if not test_infix_expression(array.elements[1], 2, '*', 2):
        return False
    if not test_infix_expression(array.elements[2], 3, '+', 3):
        return False
    return True


def test_parsing_index_expression():
    program = parse("myArray[1 + 1]")
    stmt = check_type(ExpressionStatement, program.statements[0])
    index_exp = check_type(IndexExpression, stmt.expression)
    if not test_identifier(index_exp.left, "myArray"):
        return False
    if not test_infix_expression(index_exp.index, 1, '+', 1):
        return False
    return True


def test_parsing_hash_literal_string_key():
    code = """{"one":1, "two":2, "three":3}"""
    program = parse(code)
    stmt = check_type(ExpressionStatement, program.statements[0])
    entry = check_type(HashLiteral, stmt.expression)
    check_len(3, entry.pairs)
    expected = {"one": 1, "two": 2, "three": 3}
    for (key, value) in entry.pairs.items():
        if not isinstance(key, StringLiteral):
            print(f"key is not StringLiteral. got {key}")
            return False
        if not test_integer_literal(value, expected[key.string()]):
            return False
    return True


def test_parsing_hash_literal_string_with_expressions():
    code = """{"one": 0 + 1, "two": 10 - 8, "three": 15 / 5}"""
    program = parse(code)
    stmt = check_type(ExpressionStatement, program.statements[0])
    entry = check_type(HashLiteral, stmt.expression)
    check_len(3, entry.pairs)
    expected = {"one": (0, '+', 1), "two": (10, '-', 8), "three": (15, '/', 5)}
    for key, value in entry.pairs:
        if not isinstance(key, StringLiteral):
            print(f"key is not StringLiteral. got {key}")
            return False
        if not test_infix_expression(expected[key.string()], *value):
            return False
    return True


def test_parsing_empty_hash_literal():
    code = "{}"
    program = parse(code)
    stmt = check_type(ExpressionStatement, program.statements[0])
    entry = check_type(HashLiteral, stmt.expression)
    check_len(0, entry.pairs)
    return True


def test_parsing_macro_literal():
    code = "macro(x, y) {x+y;}"
    program = parse(code)
    output = check_len(1, program.statements)
    if type(output) == tuple:
        return output
    stmt = check_type(ExpressionStatement, program.statements[0])
    if type(stmt) == tuple:
        return stmt
    macro = check_type(MacroLiteral, stmt.expression)
    if type(macro) == tuple:
        return macro
    output = check_len(2, macro.parameters)
    if type(output) == tuple:
        return output
    output = test_literal_expression(macro.parameters[0], 'x')
    if type(output) == tuple:
        return output
    output = test_literal_expression(macro.parameters[1], 'y')
    if type(output) == tuple:
        return output
    output = check_len(1, macro.body.statements)
    if type(output) == tuple:
        return output
    body_stmt = check_type(ExpressionStatement, macro.body.statements[0])
    if type(body_stmt) == tuple:
        return body_stmt
    return test_infix_expression(body_stmt.expression, "x", "+", "y")


if __name__ == '__main__':
    cases = [
        test_let_statements,
        test_return_statement,
        test_identifier_expression,
        test_integer_literal_expression,
        test_parsing_prefix_expressions,
        test_parsing_infix_expressions,
        test_operator_precedence_parsing,
        test_if_expression,
        test_if_else_expression,
        test_function_literal_parsing,
        test_function_parameter_parsing,
        test_call_expression_parsing,
        test_string_literal_expression,
        test_parsing_array_literals,
        test_parsing_index_expression,
        test_parsing_hash_literal_string_key,
        test_parsing_empty_hash_literal,
        test_parsing_macro_literal,
    ]
    run_cases(cases)
