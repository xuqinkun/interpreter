# -*- coding: utf-8 -*-
from typing import Callable, List, Tuple, Optional, Union

from monkey_evaluate.evaluator import evaluate
from monkey_lexer import lexer
from monkey_object import object
from monkey_parser.parser import Parser


def run_cases(funcs: List[Callable]):
    passed_cases = 0
    total_cases = len(funcs)
    failed_list = {}
    for func in funcs:
        output = func()
        if type(output) == tuple:
            failed_list[func.__name__] = output[1]
        else:
            passed_cases += 1
    pass_rate = passed_cases / total_cases
    print(f"{pass_rate * 100:.0f}% accepted")
    for case, cause in failed_list.items():
        print(f"Run {case} failed. Cause: {cause}")


def check_parser_errors(p: Parser):
    errors = p.errors
    if not errors:
        return False
    print(f'parser has {len(errors)} errors')
    for err in errors:
        print(f'parse error:{err}')
    return True


def check_len(expected_len: int, statements: list):
    if expected_len != len(statements):
        return False, f"Wrong statements number, expected {expected_len} got {len(statements)}"
    return True


def parse(code):
    l = lexer.get_lexer(code)
    p = Parser.get_parser(l)
    program = p.parse_program()
    check_parser_errors(p)
    return program


def check_type(expected_type: type, obj: object) -> Tuple[Union[object.Object, str], bool]:
    if isinstance(obj, object.Error):
        return obj, True
    if not isinstance(obj, expected_type):
        return f"Wrong type error, expected: {expected_type} actual:{type(obj)}", False
    return expected_type.copy(obj), True


def get_eval(code: str):
    p = Parser.get_parser(lexer.get_lexer(code))
    program = p.parse_program()
    env = object.Environment()
    return evaluate(program, env)
