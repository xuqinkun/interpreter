# -*- coding: utf-8 -*-
from object import object
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


def test_integer_object(obj: Object, expected: int):
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
    ]
    for case in cases:
        evaluated = get_eval(case[0])
        if not test_integer_object(evaluated, case[1]):
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


if __name__ == '__main__':
    tests = [
        test_eval_integer_expression,
        test_bang_operator,
    ]
    run_cases(tests)
