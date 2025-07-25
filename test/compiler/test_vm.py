from typing import List, Tuple, Union

from monkey_compiler.compiler import Compiler
from monkey_object import object
from monkey_parser import parser
from monkey_vm import vm
from monkey_vm.vm import VM
from util import test_util


def test_integer_object(expected: int, actual: object.Object):
    result, ok = test_util.check_type(expected_type=object.Integer, obj=actual)
    if not ok:
        return f"object is not Integer. got={type(actual)} ({actual})"
    if result.value != expected:
        return f"object has wrong value. got={result.value} want={expected}"
    return None


def test_boolean_object(expected: bool, actual: object.Object):
    result, ok = test_util.check_type(expected_type=object.Boolean, obj=actual)
    if not ok:
        return f"object is not Boolean. got={type(actual)} ({actual})"
    if result.value != expected:
        return f"object has wrong value. got={result.value} want={expected}"
    return None


def run_vm_test(cases: List[Tuple[str, Union[int, str, List]]]):
    for code, expected in cases:
        program = parser.parse(code)
        comp = Compiler()
        err = comp.compile(program)
        if err is not None:
            return f"compiler error: {err}"
        vm = VM.new(comp.bytecode())
        err = vm.run()
        if err is not None:
            print(f"vm error: {err}")
            return False
        stack_elem = vm.last_popped_stack_elem()
        test_expected_object(expected, stack_elem)
    return True


def test_expected_object(expected, actual: object.Object):
    exp_type = type(expected)
    if exp_type == int:
        err = test_integer_object(expected, actual)
        if err is not None:
            print(f"test_integer_object failed: {err}")
    elif exp_type == bool:
        err = test_boolean_object(expected, actual)
        if err is not None:
            print(f"test_boolean_object failed: {err}")
    elif exp_type == str:
        err = test_string_object(expected, actual)
        if err is not None:
            print(f"test_string_object failed: {err}")
    elif exp_type == object.Null:
        if actual != vm.NULL:
            print(f"object is not null: {type(actual)} {actual}")
    elif exp_type == object.Array:
        array, ok = test_util.check_type(object.Array, actual)
        if not ok:
            return f"object is not array : {type(actual)} {actual}"
        if len(array.elements) != len(expected):
            return f"wrong num of elements. want={len(expected)} got={len(array.elements)}"
        for i, expected_elem in enumerate(expected):
            err = test_integer_object(expected_elem, array.elements[i])
            if err is not None:
                print(f"test_integer_object failed: {err}")
    return f"type not supported: {exp_type}"


def test_string_object(expected:str, actual: object.Object):
    result, ok = test_util.check_type(object.String, actual)
    if not ok:
        return f"object is not String. got={type(actual)} ({actual})"
    if result.value != expected:
        return f"object has wrong value. got={result.value} want={expected}"
    return None

def test_infix_expressions():
    tests = [("1", 1),
             ("2", 2),
             ("1+2", 3),
             ("1 - 2", -1),
             ("1 * 2", 2),
             ("4 / 2", 2),
             ("50 / 2 * 2 + 10 - 5", 55),
             ("5 + 5 + 5 + 5 - 10", 10),
             ("2 * 2 * 2 * 2 * 2", 32),
             ("5 * 2 + 10", 20),
             ("5 + 2 * 10", 25),
             ("5 * (2 + 10)", 60),
             ]
    if run_vm_test(tests):
        print('Accepted')


def test_boolean_expressions():
    tests = [("true", True),
             ("false", False),
             ("!true", False),
             ("!false", True),
             ("!5", False),
             ("!!true", True),
             ("!!false", False),
             ("!!5", True),
             ("1 < 2", True),
             ("1 > 2", False),
             ("1 < 1", False),
             ("1 > 1", False),
             ("1 == 1", True),
             ("1 != 1", False),
             ("1 == 2", False),
             ("1 != 2", True),
             ("true == true", True),
             ("false == false", True),
             ("true == false", False),
             ("true != false", True),
             ("false != true", True),
             ("(1 < 2) == true", True),
             ("(1 < 2) == false", False),
             ("(1 > 2) == true", False),
             ("(1 > 2) == false", True),
             ("!(if (false) { 5; })", True)
             ]
    if run_vm_test(tests) is True:
        print('test_boolean_expressions Accepted')


def test_integer_arithmetic():
    tests = [("-5", -5),
             ("-10", -10),
             ("-50+100+-50", 0),
             ("(5+10*2+15/3) * 2 + -10", 50)
             ]
    if run_vm_test(tests) is True:
        print('test_integer_arithmetic Accepted')

def test_conditionals():
    tests = [
        ("if (true) { 10 }", 10),
        ("if (true) { 10 } else { 20 }", 10),
        ("if (false) { 10 } else { 20 } ", 20),
        ("if (1) { 10 }", 10),
        ("if (1 < 2) { 10 }", 10),
        ("if (1 < 2) { 10 } else { 20 }", 10),
        ("if (1 > 2) { 10 } else { 20 }", 20),
        ("if (1 > 2) { 10 }", vm.NULL),
        ("if (false) { 10 }", vm.NULL),
        ("if ((if (false) { 10 })) { 10 } else { 20 }", 20),
    ]
    if run_vm_test(tests) is True:
        print('test_conditionals Accepted')

def test_global_let_statements():
    tests =[
        ("let one = 1; one", 1),
        ("let one = 1; let two = 2; one + two", 3),
        ("let one = 1; let two = one + one; one + two", 3)]
    if run_vm_test(tests) is True:
        print('test_global_let_statements Accepted')


def test_string_expressions():
    cases = [
        ('"monkey"', "monkey"),
        ('"mon" + "key"', "monkey"),
        ('"mon" + "key" + "banana"', "monkeybanana"),
    ]
    if run_vm_test(cases) is True:
        print('test_global_let_statements Accepted')


def test_array_expressions():
    cases = [
        ('[]', []),
        ('[1,2,3]', [1,2,3]),
        ('[1+2,3*4,5+6]', [3,12,11]),
    ]
    if run_vm_test(cases) is True:
        print('test_array_expressions Accepted')


if __name__ == '__main__':
    test_integer_arithmetic()
    test_boolean_expressions()
    test_conditionals()
    test_global_let_statements()
    test_string_expressions()
    test_array_expressions()