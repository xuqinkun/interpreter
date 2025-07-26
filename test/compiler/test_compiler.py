from typing import List, Tuple
from monkey_parser import parser
from monkey_code import code
from monkey_compiler.compiler import Compiler
from monkey_object import object
from util import test_util

def concat_instructions(instructions_list: List[code.Instructions]):
    return code.Instructions(b''.join(instructions_list))


def test_instructions(expected: List[code.Instructions], actual: code.Instructions):
    concat = concat_instructions(expected)
    if len(actual) != len(concat):
        return f"wrong instructions length.\n want={str(concat)} got={str(actual)}"
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
        err = test_instructions(expected_instructions, code.Instructions(bytecode.instructions))
        if err is not None:
            return False, f"test_instructions failed: {err}"
        err = test_constants(expected_constants, bytecode.constants)
        if err is not None:
            return False, f"test_constants failed: {err}"
    return None

def test_integer_arithmetic():
    cases = [
        ("1+2", (1, 2), [code.make(code.OpConstant, 0),
                        code.make(code.OpConstant, 1),
                         code.make(code.OpAdd),
                         code.make(code.OpPop)]),
        ("1;2", (1, 2), [code.make(code.OpConstant, 0),
                         code.make(code.OpPop),
                         code.make(code.OpConstant, 1),
                         code.make(code.OpPop)]),
        ("1-2", (1, 2), [code.make(code.OpConstant, 0),
                         code.make(code.OpConstant, 1),
                         code.make(code.OpSub),
                         code.make(code.OpPop)]),
        ("1*2", (1, 2), [code.make(code.OpConstant, 0),
                         code.make(code.OpConstant, 1),
                         code.make(code.OpMul),
                         code.make(code.OpPop)]),
        ("2/1", (2, 1), [code.make(code.OpConstant, 0),
                         code.make(code.OpConstant, 1),
                         code.make(code.OpDiv),
                         code.make(code.OpPop)]),
        ("-1", (1,), [code.make(code.OpConstant, 0),
                         code.make(code.OpMinus),
                         code.make(code.OpPop)]),
    ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True


def test_boolean_expressions():
    cases = [
        ("true", (), (code.make(code.OpTrue), code.make(code.OpPop))),
        ("false", (), (code.make(code.OpFalse), code.make(code.OpPop))),
        ("!true", (), (code.make(code.OpTrue),
                       code.make(code.OpBang),
                       code.make(code.OpPop))),
        ("1>2", (1,2), (
                       code.make(code.OpConstant, 0),
                       code.make(code.OpConstant, 1),
                       code.make(code.OpGreaterThan),
                       code.make(code.OpPop))),
        ("1<2", (2,1), (
                       code.make(code.OpConstant, 0),
                       code.make(code.OpConstant, 1),
                       code.make(code.OpGreaterThan),
                       code.make(code.OpPop))),
        ("1==2", (1,2), (
                       code.make(code.OpConstant, 0),
                       code.make(code.OpConstant, 1),
                       code.make(code.OpEqual),
                       code.make(code.OpPop))),
        ("1!=2", (1,2), (
                       code.make(code.OpConstant, 0),
                       code.make(code.OpConstant, 1),
                       code.make(code.OpNotEqual),
                       code.make(code.OpPop))),
        ("true==false", (), (
                       code.make(code.OpTrue),
                       code.make(code.OpFalse),
                       code.make(code.OpEqual),
                       code.make(code.OpPop))),
        ("true!=false", (), (
                       code.make(code.OpTrue),
                       code.make(code.OpFalse),
                       code.make(code.OpNotEqual),
                       code.make(code.OpPop))),
    ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True


def test_conditionals():
    cases = [
        ('if(true) {10};3333;', (10, 3333), (
           code.make(code.OpTrue),
           code.make(code.OpJumpNotTruthy, 10),
           code.make(code.OpConstant, 0),
           code.make(code.OpJump, 11),
           code.make(code.OpNull),
           code.make(code.OpPop),
           code.make(code.OpConstant, 1),
           code.make(code.OpPop)
        )),
        ('if (true) { 10 } else { 20 }; 3333;',  (10, 20, 3333), (
            code.make(code.OpTrue),
            code.make(code.OpJumpNotTruthy, 10),
            code.make(code.OpConstant, 0),
            code.make(code.OpJump, 13),
            code.make(code.OpConstant, 1),
            code.make(code.OpPop),
            code.make(code.OpConstant, 2),
            code.make(code.OpPop)
        )),
        ('if (true) { 10 }; 3333;',  (10, 3333), (
            code.make(code.OpTrue),
            code.make(code.OpJumpNotTruthy, 10),
            code.make(code.OpConstant, 0),
            code.make(code.OpJump, 11),
            code.make(code.OpNull),
            code.make(code.OpPop),
            code.make(code.OpConstant, 1),
            code.make(code.OpPop)
        ))]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True

def test_global_let_statements():
    cases = [("let one = 1; let two = 2;", (1,2),
              (code.make(code.OpConstant, 0),
               code.make(code.OpSetGlobal, 0),
               code.make(code.OpConstant, 1),
               code.make(code.OpSetGlobal, 1)
               )
              ),
             ("let one = 1; one;", (1,),
              (code.make(code.OpConstant, 0),
               code.make(code.OpSetGlobal, 0),
               code.make(code.OpGetGlobal, 0),
               code.make(code.OpPop)
               )
              ),
             ("let one = 1; let two = one; two;", (1,),
              (code.make(code.OpConstant, 0),
               code.make(code.OpSetGlobal, 0),
               code.make(code.OpGetGlobal, 0),
               code.make(code.OpSetGlobal, 1),
               code.make(code.OpGetGlobal, 1),
               code.make(code.OpPop)
               )
              )
             ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True


def test_string_expressions():
    cases = [
        ('"monkey"', ("monkey",), (code.make(code.OpConstant, 0), code.make(code.OpPop))),
        ('"mon"+"key"', ("mon", "key"), (code.make(code.OpConstant, 0),
                                         code.make(code.OpConstant, 1),
                                         code.make(code.OpAdd),
                                         code.make(code.OpPop)
                                         )),
    ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True


def test_string_object(expected: str, actual: object.Object):
    result, ok = test_util.check_type(object.String, actual)
    if not ok:
        return f"object is not String. got={type(actual)} {actual}"
    if result.value != expected:
        return f"object has wrong value. got={result.value}, want={expected}"
    return None


def test_array_literals():
    cases = [
        ("[]", (), (code.make(code.OpArray, 0), code.make(code.OpPop))),
        ("[1,2,3]", (1,2,3), (code.make(code.OpConstant, 0),
                              code.make(code.OpConstant, 1),
                              code.make(code.OpConstant, 2),
                              code.make(code.OpArray, 3),
                              code.make(code.OpPop))),
        ("[1+2,3-4,5*6]", (1,2,3,4,5,6),
                            (code.make(code.OpConstant, 0),
                              code.make(code.OpConstant, 1),
                              code.make(code.OpAdd),
                              code.make(code.OpConstant, 2),
                              code.make(code.OpConstant, 3),
                              code.make(code.OpSub),
                              code.make(code.OpConstant, 4),
                              code.make(code.OpConstant, 5),
                              code.make(code.OpMul),
                              code.make(code.OpArray, 3),
                              code.make(code.OpPop))),
             ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True

def test_hash_literals():
    cases = [
        ("{}", (), (code.make(code.OpHash, 0), code.make(code.OpPop))),
        ("{1:2, 3:4, 5:6}", (1,2,3,4,5,6), (code.make(code.OpConstant, 0),
                             code.make(code.OpConstant, 1),
                             code.make(code.OpConstant, 2),
                             code.make(code.OpConstant, 3),
                             code.make(code.OpConstant, 4),
                             code.make(code.OpConstant, 5),
                             code.make(code.OpHash, 6),
                             code.make(code.OpPop),
                             )
         ),
        ("{1:2+3, 4: 5*6}", (1, 2, 3, 4, 5, 6), (code.make(code.OpConstant, 0),
                                                 code.make(code.OpConstant, 1),
                                                 code.make(code.OpConstant, 2),
                                                 code.make(code.OpAdd),
                                                 code.make(code.OpConstant, 3),
                                                 code.make(code.OpConstant, 4),
                                                 code.make(code.OpConstant, 5),
                                                 code.make(code.OpMul),
                                                 code.make(code.OpHash, 4),
                                                 code.make(code.OpPop),
                                                 )
         ),
             ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True


def test_index_expressions():
    cases = [
        ("[1,2,3][1 + 1]", (1,2,3,1,1),
            (
             code.make(code.OpConstant, 0),
             code.make(code.OpConstant, 1),
             code.make(code.OpConstant, 2),
             code.make(code.OpArray, 3),
             code.make(code.OpConstant, 3),
             code.make(code.OpConstant, 4),
             code.make(code.OpAdd),
             code.make(code.OpIndex),
             code.make(code.OpPop),
            )
         ),
        ("{1:2}[2-1]", (1, 2, 2, 1), (code.make(code.OpConstant, 0),
                                                 code.make(code.OpConstant, 1),
                                                 code.make(code.OpHash, 2),
                                                 code.make(code.OpConstant, 2),
                                                 code.make(code.OpConstant, 3),
                                                 code.make(code.OpSub),
                                                 code.make(code.OpIndex),
                                                 code.make(code.OpPop),
                                                 )
         ),
    ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True

if __name__ == '__main__':
    tests = [
        test_integer_arithmetic,
        test_boolean_expressions,
        test_conditionals,
        test_global_let_statements,
        test_string_expressions,
        test_array_literals,
        test_hash_literals,
        test_index_expressions
    ]
    test_util.run_cases(tests)


