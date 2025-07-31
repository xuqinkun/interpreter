from typing import List, Tuple, Union, Dict

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


def run_vm_test(cases: List[Tuple[str, Union[int, str, List, Dict]]]):
    for code, expected in cases:
        program = parser.parse(code)
        comp = Compiler()
        err = comp.compile(program)
        if err is not None:
            return f"compiler error: {err}"
        vm = VM(comp.bytecode())
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
    elif exp_type == object.HashKey:
        h, ok = test_util.check_type(object.Hash, actual)
        if not ok:
            return f"object is not hash. got={type(actual)} {actual}"
        if len(h.pairs) != len(expected):
            return f"hash has wrong num of pairs. want={len(expected)} got={len(h.pairs)}"
        for k, v in expected.items():
            if k not in h.pairs:
                print(f"no pair for given key in pairs")
            pair = h.pairs[k]
            err = test_integer_object(v, pair.value)
            if err is not None:
                print(f"test_integer_object failed: {err}")
    return f"type not supported: {exp_type}"


def test_string_object(expected: str, actual: object.Object):
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
    tests = [
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
        ('[1,2,3]', [1, 2, 3]),
        ('[1+2,3*4,5+6]', [3, 12, 11]),
    ]
    if run_vm_test(cases) is True:
        print('test_array_expressions Accepted')


def test_hash_literals():
    cases = [("{}", {}),
             ("{1:2, 2:3}", {object.Integer(value=1).hash_key(): 2,
                             object.Integer(value=2).hash_key(): 3}),
             ("{1+1:2*2, 3+3:4*4}", {object.Integer(value=2).hash_key(): 4,
                                     object.Integer(value=6).hash_key(): 16}),
             ]
    if run_vm_test(cases) is True:
        print('test_hash_literals Accepted')


def test_index_expressions():
    cases = [
        ("[1, 2, 3][1]", 2),
        ("[1, 2, 3][0 + 2]", 3),
        ("[[1, 1, 1]][0][0]", 1),
        ("[][0]", object.NULL),
        ("[1, 2, 3][99]", object.NULL),
        ("[1][-1]", object.NULL),
        ("{1: 1, 2: 2}[1]", 1),
        ("{1: 1, 2: 2}[2]", 2),
        ("{1: 1}[0]", object.NULL),
        ("{}[0]", object.NULL),
    ]
    if run_vm_test(cases) is True:
        print('test_index_expressions Accepted')


def test_calling_functions_without_arguments():
    cases = [
        ('let fivePlusTen = fn() {5+10};fivePlusTen();', 15),
        ('let one = fn() { 1; };let two = fn() { 2; };one() + two()', 3),
        ('let a = fn() { 1 };let b = fn() { a() + 1 };let c = fn() { b() + 1 };c();', 3),
        ("""
        let earlyExit = fn() { return 99; 100; };
        earlyExit();
        """, 99),
        ("""
        let earlyExit = fn() { return 99; return 100; };
        earlyExit();
        """, 99),
    ]
    if run_vm_test(cases) is True:
        print('test_calling_functions_without_arguments Accepted')


def test_calling_functions_without_return_value():
    cases = [
        ("""
        let noReturn = fn() { };
        noReturn();
        """, object.NULL),
        ("""
        let noReturn = fn() { };
        let noReturnTwo = fn() { noReturn(); };
        noReturn();
        noReturnTwo();
        """, object.NULL),
    ]
    if run_vm_test(cases) is True:
        print('test_calling_functions_without_return_value Accepted')


def test_first_class_functions():
    cases = [
        ("""
        let returnsOne = fn() { 1; };
        let returnsOneReturner = fn() { returnsOne; };
        returnsOneReturner()();
        """, 1),
        ("""
        let returnsOneReturner = fn() {
            let returnsOne = fn() { 1; };
            returnsOne;
        };
        returnsOneReturner()();
        """, 1),
    ]
    if run_vm_test(cases) is True:
        print('test_first_class_functions Accepted')


def test_calling_functions_with_bindings():
    cases = [
        ("""
        let one = fn() { let one = 1; one };
        one();
        """, 1),
        ("""
        let oneAndTwo = fn() { let one = 1; let two = 2; one + two; };
        oneAndTwo();
        """, 3),
        ("""
        let oneAndTwo = fn() { let one = 1; let two = 2; one + two; };
        let threeAndFour = fn() { let three = 3; let four = 4; three + four; };
        oneAndTwo() + threeAndFour();
        """, 10),
        ("""
        let firstFoobar = fn() { let foobar = 50; foobar; };
        let secondFoobar = fn() { let foobar = 100; foobar; };
        firstFoobar() + secondFoobar();
        """, 150),
        ("""
        let globalSeed = 50;
        let minusOne = fn() {
            let num = 1;
            globalSeed - num;
        }
        let minusTwo = fn() {
            let num = 2;
            globalSeed - num;
        }
        minusOne() + minusTwo();
        """, 97),
    ]
    if run_vm_test(cases) is True:
        print('test_calling_functions_with_bindings Accepted')


def test_calling_functions_with_arguments_and_bindings():
    cases = [
        ("""
        let identity = fn(a) { a; };
        identity(4);
        """, 4),
        ("""
        let sum = fn(a, b) { a + b; };
        sum(1, 2);
        """, 3),
        ("""
        let sum = fn(a, b) {
            let c = a + b;
            c;
        };
        sum(1, 2);
        """, 3),
        ("""
        let sum = fn(a, b) {
            let c = a + b;
            c;
        };
        sum(1, 2) + sum(3, 4);
        """, 10),
        ("""
        let sum = fn(a, b) {
            let c = a + b;
            c;
        };
        let outer = fn() {
            sum(1, 2) + sum(3, 4);
        };
        outer();
        """, 10),
        ("""
        let globalNum = 10;

        let sum = fn(a, b) {
            let c = a + b;
            c + globalNum;
        };

        let outer = fn() {
            sum(1, 2) + sum(3, 4) + globalNum;
        };

        outer() + globalNum;
        """, 50),
    ]
    if run_vm_test(cases) is True:
        print('test_calling_functions_with_arguments_and_bindings accepted')


def test_calling_functions_with_wrong_arguments():
    cases = [
        ("fn() { 1; }(1);", "wrong number of arguments: want=0, got=1"),
        ("fn(a) { a; }();", "wrong number of arguments: want=1, got=0"),
        ("fn(a, b) { a + b; }(1);", "wrong number of arguments: want=2, got=1"),
    ]

    for code, expected in cases:
        program = parser.parse(code)
        comp = Compiler()
        err = comp.compile(program)
        if err is not None:
            return f"compiler error: {err}"
        vm = VM(comp.bytecode())
        err = vm.run()
        if err is None:
            print("expected VM error but resulted in none.")
        if err != expected:
            print(f"wrong VM error: want={expected}, got={err}")


if __name__ == '__main__':
    test_integer_arithmetic()
    test_boolean_expressions()
    test_conditionals()
    test_global_let_statements()
    test_string_expressions()
    test_array_expressions()
    test_hash_literals()
    test_index_expressions()
    test_calling_functions_without_arguments()
    test_calling_functions_without_return_value()
    test_first_class_functions()
    test_calling_functions_with_bindings()
    test_calling_functions_with_arguments_and_bindings()
    test_calling_functions_with_wrong_arguments()
