from typing import List, Tuple
from monkey_vm.vm import VM
from util import test_util
from monkey_object import object
from monkey_parser import parser
from monkey_compiler.compiler import Compiler


def test_integer_object(expected: int, actual: object.Object):
    result, ok = test_util.check_type(expected_type=object.Integer, obj=actual)
    if not ok:
        return f"object is not integer. got={type(actual)} ({actual})"
    if result.value != expected:
        return f"object has wrong value. got={result.value} want={expected}"
    return None


def run_vm_test(cases: List[Tuple[str, int]]):
    for code, expected in cases:
        program = parser.parse(code)
        comp = Compiler()
        err = comp.compile(program)
        if err is not None:
            return f"compiler error: {err}"
        vm = VM.new(comp.bytecode())
        err = vm.run()
        if err is not None:
            return f"vm error: {err}"
        stack_elem = vm.peek()
        test_expected_object(expected, stack_elem)


def test_expected_object(expected, actual: object.Object):
    if type(expected) == int:
        err = test_integer_object(expected, actual)
        if err is not None:
            print(f"test_integer_object failed: {err}")


if __name__ == '__main__':
    tests = [("1", 1), ("2", 2), ("1+2", 2)]
    run_vm_test(tests)
