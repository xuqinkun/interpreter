# -*- coding: utf-8 -*-
from monkey_object import object
from monkey_evaluate import evaluator
from monkey_parser.parser import *
from monkey_object.object import *
from util import test_util


def test_integer_object(expected: int, obj: Object):
    output, ok = test_util.check_type(Integer, obj)
    if not ok:
        return output
    result = output
    if result.value != expected:
        cause = f"object has wrong value, got:{result.value} expected: {expected}"
        return False, cause
    return True


def test_eval_integer_expression():
    cases = [
        ("5", 5),
        ("10", 10),
        ("-5", -5),
        ("-10", -10),
        ("5 + 5 + 5 + 5 - 10", 10),
        ("2 * 2 * 2 * 2 * 2", 32),
        ("-50 + 100 + -50", 0),
        ("5 * 2 + 10", 20),
        ("5 + 2 * 10", 25),
        ("20 + 2 * -10", 0),
        ("50 / 2 * 2 + 10", 60),
        ("2 * (5 + 10)", 30),
        ("3 * 3 * 3 + 10", 37),
        ("3 * (3 * 3) + 10", 37),
        ("(5 + 10 * 2 + 15 / 3) * 2 + -10", 50),
    ]
    for case in cases:
        evaluated = test_util.get_eval(case[0])
        output = test_integer_object(case[1], evaluated)
        if type(output) == tuple:
            return output
    return True


def test_eval_boolean_expression():
    cases = [
        ("1 < 2", True),
        ("1 > 2", False),
        ("1 < 1", False),
        ("1 > 1", False),
        ("1 == 1", True),
        ("1 != 1", False),
        ("1 == 2", False),
        ("1 != 2", True),
        ("true == true", True),
        ("true && true", True),
        ("false == false", True),
        ("false || false", False),
        ("true == false", False),
        ("true != false", True),
        ("false != true", True),
        ("(1 < 2) == true", True),
        ("(1 < 2) == false", False),
        ("(1 > 2) == true", False),
        ("(1 > 2) == false", True),
        ("(1 > 2) && false", False),
        ("(1 > 2) || false", False),
    ]
    for case in cases:
        ret = test_util.get_eval(case[0])
        output = test_boolean_object(ret, case[1])
        if type(output) == tuple:
            return output
    return True


def test_null_object(obj: object.Object):
    if obj != evaluator.NULL:
        return False, f'obj is not NULL, got: {type(obj)}:{obj}'
    return True


def test_if_else_expression():
    cases = [
        ("if (true) { 10 }", 10),
        ("if (false) { 10 }", NULL),
        ("if (1) { 10 }", 10),
        ("if (1 < 2) { 10 }", 10),
        ("if (1 > 2) { 10 }", NULL),
        ("if (1 > 2) { 10 } else { 20 }", 20),
        ("if (1 < 2) { 10 } else { 20 }", 10),
        ("""
            if (10 > 1) {
              if (10 > 1) {
                return 10;
              }
            
              return 1;
          }
        """, 10),
    ]
    for case in cases:
        ret = test_util.get_eval(case[0])
        if case[1] == NULL:
            output = test_null_object(ret)
        else:
            output = test_integer_object(case[1], ret)
        if type(output) == tuple:
            return output
    return True


def test_bang_operator():
    cases = [
        ("!true", False),
        ("!false", True),
        ("!5", False),
        ("!!true", True),
        ("!!false", False),
        ("!!5", True),
        ("!0", True),
    ]
    for cpde, expected in cases:
        ret = test_util.get_eval(cpde)
        ret = test_boolean_object(ret, expected)
        if type(ret) == tuple:
            return ret
    return True


def test_boolean_object(obj: Object, expected: bool):
    output, ok = test_util.check_type(object.Boolean, obj)
    if not ok:
        return output
    result = output
    if result.value != expected:
        cause = f"result.value has wrong value, got:{result.value} expected: {expected}"
        return False, cause
    return True


def test_return_statements():
    cases = [
        ("return 10;", 10),
        ("return 10; 9;", 10),
        ("return 2 * 5; 9;", 10),
        ("9; return 2 * 5; 9;", 10),
    ]
    for case in cases:
        ret = test_util.get_eval(case[0])
        output = test_integer_object(case[1], ret)
        if type(output) == tuple:
            return output
    return True


def test_error_handling():
    cases = [
        (
            "5 + true;",
            "type mismatch: INTEGER + BOOLEAN",
        ),
        (
            "5 + true; 5;",
            "type mismatch: INTEGER + BOOLEAN",
        ),
        (
            "-true",
            "unknown operator: -BOOLEAN",
        ),
        (
            "true + false;",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            "5; true + false; 5",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            "if (10 > 1) { true + false; }",
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        (
            """
    if (10 > 1) {
        if (10 > 1) {
        return true + false;
        }
    
        return 1;
    }
    """,
            "unknown operator: BOOLEAN + BOOLEAN",
        ),
        ("x", "identifier not found: x"),
        ('"Hello"-"world!"', "unknown operator: STRING - STRING"),
    ]
    for code, expected in cases:
        ret = test_util.get_eval(code)
        if not isinstance(ret, Error):
            print(f'no error obj returned,got: {type(ret)}:{ret}')
            continue
        if ret.message != expected:
            return False, f"expected:{expected} got: {ret.message}"
    return True


def test_let_statements():
    cases = [
        ("let a = 5; a;", 5),
        ("let a = 5 * 5; a;", 25),
        ("let a = 5; let b = a; b;", 5),
        ("let a = 5; let b = a; let c = a + b + 5; c;", 15),
    ]
    for case in cases:
        ret = test_util.get_eval(case[0])
        output = test_integer_object(case[1], ret)
        if type(output) == tuple:
            return output
    return True


def test_function_object():
    code = 'fn(x) { x + 2; };'
    ret = test_util.get_eval(code)
    fn, _ = test_util.check_type(object.Function, ret)
    parameters = fn.parameters
    if len(parameters) != 1:
        return False, f'function has wrong params, params: {parameters}'
    if parameters[0].string() != 'x':
        return False, f"parameter is not 'x', got: {parameters[0]}"
    expected_body = '(x + 2)'
    if fn.body.string() != expected_body:
        return False, f"body is not {expected_body}, got {fn.body.string()}"
    return True


def test_string_literal():
    code = '"Hello world!"'
    ret = test_util.get_eval(code)
    string, ok = test_util.check_type(object.String, ret)
    if string.value != "Hello world!":
        return False, f'String has wrong value, got {string.value}'
    return True


def test_string_concat():
    code = '"Hello" + " " + "world!'
    ret = test_util.get_eval(code)
    output, ok = test_util.check_type(object.String, ret)
    if not ok:
        return output
    string = output
    if string.value != "Hello world!":
        return False, f'String has wrong value, got {string.value}'
    return True


def test_function_application():
    cases = [
        ("let identity = fn(x) { x; }; identity(5);", 5),
        ("let identity = fn(x) { return x; }; identity(5);", 5),
        ("let double = fn(x) { x * 2; }; double(5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5, 5);", 10),
        ("let add = fn(x, y) { x + y; }; add(5 + 5, add(5, 5));", 20),
        ("fn(x) { x; }(5)", 5),
    ]
    for case in cases:
        ret = test_util.get_eval(case[0])
        if not test_integer_object(case[1], ret):
            return False
    return True


def test_builtin_functions():
    cases = [
        ('len("")', 0),
        ('len("four")', 4),
        ('len("hello world")', 11),
        ('len(1)', "argument to 'len' not supported, got INTEGER"),
        ('len("one", "two")', "wrong number of arguments. got 2, want 1"),
    ]
    for case in cases:
        ret = test_util.get_eval(case[0])
        if isinstance(case[1], int):
            if not test_integer_object(case[1], ret):
                return False
        else:
            error, ok = test_util.check_type(Error, ret)
            if error.message != case[1]:
                print(f'wrong error message. expected "{case[1]}" got "{error.message}"')
                return False
    return True


def test_array_literal():
    code = "[1, 2*2, 3+3]"
    ret = test_util.get_eval(code)
    if not isinstance(ret, Array):
        print(f"object is not Array, got {type(ret)} {ret}")
        return False
    if len(ret.elements) != 3:
        print(f"array has wrong num of elements, got {len(ret.elements)}")
        return False
    if not test_integer_object(1, ret.elements[0]):
        return False
    if not test_integer_object(4, ret.elements[1]):
        return False
    if not test_integer_object(6, ret.elements[2]):
        return False
    return True


def test_array_index_expression():
    cases = [
        (
            "[1, 2, 3][0]",
            1,
        ),
        (
            "[1, 2, 3][1]",
            2,
        ),
        (
            "[1, 2, 3][2]",
            3,
        ),
        (
            "let i = 0; [1][i];",
            1,
        ),
        (
            "[1, 2, 3][1 + 1];",
            3,
        ),
        (
            "let myArray = [1, 2, 3]; myArray[2];",
            3,
        ),
        (
            "let myArray = [1, 2, 3]; myArray[0] + myArray[1] + myArray[2];",
            6,
        ),
        (
            "let myArray = [1, 2, 3]; let i = myArray[0]; myArray[i]",
            2,
        ),
        (
            "[1, 2, 3][3]",
            NULL,
        ),
        (
            "[1, 2, 3][-1]",
            NULL,
        ),
    ]
    for (code, expected) in cases:
        ret = test_util.get_eval(code)
        if type(expected) == int:
            passed = test_integer_object(expected, ret)
        else:
            passed = test_null_object(ret)
        if not passed:
            return False
    return True


def test_hash_literal():
    code = """let two = "two";
        {"one": 10 - 9,
        two: 1 + 1,
        "thr" + "ee": 6 / 2,
        4: 4,
        true: 5,
        false: 6}
    """
    ret = test_util.get_eval(code)
    if not isinstance(ret, Hash):
        print(f"eval didn't return Hash. got {type(ret)}:{ret}")
        return False
    expected = {
        String("one").hash_key(): 1,
        String("two").hash_key(): 2,
        String("three").hash_key(): 3,
        Integer(4).hash_key(): 4,
        TRUE.hash_key(): 5,
        FALSE.hash_key(): 6,
    }
    if len(expected) != len(ret.pairs):
        print(f"Hash has wrong num of pairs. got {len(ret.pairs)}")
        return False
    for exp_key, exp_val in expected.items():
        pair = ret.pairs.get(exp_key, None)
        if pair is None:
            print(f"no pair for given key[{exp_key}] in pairs")
            return False
        if not test_integer_object(exp_val, pair.value):
            return False
    return True


def test_hash_index_expression():
    cases = [
        (
            '{"foo": 5}["foo"]', 5),
        (
            '{"foo": 5}["bar"]',
            None,
        ), (
            'let key = "foo"; {"foo": 5}[key]',
            5,
        ), (
            '{}["foo"]',
            None,
        ), (
            '{5: 5}[5]',
            5,
        ), (
            '{true: 5}[true]',
            5,
        ), (
            '{false: 5}[false]',
            5,
        ),
    ]
    for code, expected in cases:
        ret = test_util.get_eval(code)
        if type(expected) == int:
            status = test_integer_object(expected, ret)
        else:
            status = test_null_object(ret)
        if not status:
            return False
    return True


if __name__ == '__main__':
    tests = [
        test_eval_integer_expression,
        test_bang_operator,
        test_eval_boolean_expression,
        test_if_else_expression,
        test_return_statements,
        test_error_handling,
        test_let_statements,
        test_function_object,
        test_function_application,
        test_string_literal,
        test_string_concat,
        test_builtin_functions,
        test_array_literal,
        test_array_index_expression,
        test_hash_literal,
        test_hash_index_expression
    ]
    test_util.run_cases(tests)
