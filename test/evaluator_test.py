# -*- coding: utf-8 -*-
from object import object
from evaluate import evaluator
from lexer.lexer import get_lexer
from monkey_parser.parser import *
from evaluate.evaluator import evaluate
from object.object import *


def check_type(expected_type: type, obj: object):
    if not isinstance(obj, expected_type):
        raise Exception(f"Wrong type error, expected: {expected_type} actual:{type(obj)}")
    return expected_type.copy(obj)


def get_eval(code: str):
    p = Parser.get_parser(get_lexer(code))
    program = p.parse_program()
    return evaluate(program)


def test_integer_object(expected: int, obj: Object):
    result = check_type(Integer, obj)
    if result.value != expected:
        print(f"object has wrong value, got:{result.value} expected: {expected}")
        return False
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
        evaluated = get_eval(case[0])
        if not test_integer_object(case[1], evaluated):
            return False
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
        ret = get_eval(case[0])
        if not test_boolean_object(ret, case[1]):
            return False
    return True


def test_null_object(obj: object.Object):
    if obj != evaluator.NULL:
        print(f'obj is not NULL, got: {type(obj)}:{obj}')
        return False
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
    ]
    for case in cases:
        ret = get_eval(case[0])
        if case[1] == NULL:
            exe_ret = test_null_object(ret)
        else:
            exe_ret = test_integer_object(case[1], ret)
        if not exe_ret:
            return False
    return True


def run_cases(func_list: list[Callable]):
    for func in func_list:
        func_name = func.__name__
        if func():
            print(f"Run case[{func_name}] passed")
        else:
            print(f"Run case[{func_name}] failed")


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
    for case in cases:
        ret = get_eval(case[0])
        if not test_boolean_object(ret, case[1]):
            return False
    return True


def test_boolean_object(obj: Object, expected: bool):
    result = check_type(object.Boolean, obj)
    if result.value != expected:
        print(f"result.value has wrong value, got:{result.value} expected: {expected}")
        return False
    return True


def test_return_statements():
    cases = [
        ("return 10;", 10),
        ("return 10; 9;", 10),
        ("return 2 * 5; 9;", 10),
        ("9; return 2 * 5; 9;", 10),
    ]
    for case in cases:
        ret = get_eval(case[0])
        if not test_integer_object(case[1], ret):
            return False
    return True


if __name__ == '__main__':
    tests = [
        test_eval_integer_expression,
        test_bang_operator,
        test_eval_boolean_expression,
        test_if_else_expression,
        test_return_statements,
    ]
    run_cases(tests)
