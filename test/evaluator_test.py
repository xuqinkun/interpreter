# -*- coding: utf-8 -*-
from lexer.lexer import get_lexer
from monkey_parser.parser import *
from evaluate.evaluator import evaluate
from object.object import *


def check_type(expected_type: type, obj: object):
    if not isinstance(obj, expected_type):
        raise Exception(f"Wrong type error, expected: {expected_type} actual:{type(obj)}")
    return expected_type.copy(obj)


def test_eval(code: str):
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
    ]
    for case in cases:
        evaluated = test_eval(case[0])
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


if __name__ == '__main__':
    cases = [
        test_eval_integer_expression
    ]
    run_cases(cases)
