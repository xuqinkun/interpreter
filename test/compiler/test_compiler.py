from typing import List, Tuple
from monkey_parser import parser
from monkey_code import code
from monkey_compiler.compiler import Compiler
from monkey_object import object
from util import test_util

def concat_instructions(instructions_list: List[code.Instructions]):
    out = []
    for ins in instructions_list:
        out.append(ins.string())
    return ''.join(out)


def test_instructions(expected: List[code.Instructions], actual: code.Instructions):
    concat = concat_instructions(expected)
    if len(actual) != len(concat):
        return f"wrong instructions length.\n want={concat} got={actual}"
    for i, ins in enumerate(concat):
        if actual[i] != ins:
            return f"wrong instruction at {i}. want={concat} got={actual}"
    return None


def test_integer_object(expected: int, actual: object.Object):
    result, ok = test_util.check_type(expected_type=object.Integer, obj=actual)
    if not ok:
        return f"object is not integer. got={type(actual)} ({actual})"
    if result.value != expected:
        return f"object has wrong value. got={result.value} want={expected}"
    return None


def test_constants(expected: List, actual: List[object.Object]):
    if len(expected) != len(actual):
        return False, f"wrong number of constants. got={len(actual)} want={len(expected)}"
    for i, constant in enumerate(expected):
        c_type = type(constant)
        if c_type == int:
            err = test_integer_object(constant, actual[i])
            if err is not None:
                return f"constant {i}: test_integer_object failed: {err}"
    return None


def run_compiler_tests(cases: List[Tuple]):
    for text, expected_constants, expected_instructions in cases:
        program = parser.parse(text)
        compiler = Compiler()
        err = compiler.compile(program)
        if err is not None:
            return False, f"compile error: {err}"
        bytecode = compiler.bytecode()
        err = test_instructions(expected_instructions, bytecode.instructions)
        if err is not None:
            return False, f"test_instructions failed: {err}"
        err = test_constants(expected_constants, bytecode.constants)
        if err is not None:
            return False, f"test_constants failed: {err}"
    return None

def test_integer_arithmetic():
    cases = [
        ("1+2", {1, 2}, [code.make(code.OpConstant, 0),
                        code.make(code.OpConstant, 1)])
    ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True


if __name__ == '__main__':
    cases = [
        test_integer_arithmetic
    ]
    test_util.run_cases(cases)


