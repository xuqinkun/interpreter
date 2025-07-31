from typing import List, Tuple, Union
from monkey_parser import parser
from monkey_code import code
from monkey_compiler.compiler import Compiler
from monkey_object import object
from util import test_util

def concat_instructions(instructions: Union[List[code.Instructions], bytearray]):
    if isinstance(instructions, (bytearray, bytes)):
        return code.Instructions(instructions)
    return code.Instructions(b''.join(instructions))


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
        actual_obj = actual[i]
        if c_type == int:
            err = test_integer_object(constant, actual_obj)
            if err is not None:
                return f"constant {i}: test_integer_object failed: {err}"
        elif c_type == code.Instructions:
            if not isinstance(actual_obj, object.CompiledFunction):
                return f"constant {i} not a function: {actual_obj}"
            err = test_instructions(constant, actual[i].instructions)
            if err is not None:
                return f"constant {i}: test_instructions failed: {err}"
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


def test_functions():
    cases = [
        ("fn() {return 5+10}", (5, 10, code.Instructions(b''.join([code.make(code.OpConstant, 0),
                                        code.make(code.OpConstant, 1),
                                        code.make(code.OpAdd),
                                        code.make(code.OpReturnValue)]))),
         (code.make(code.OpConstant, 2), code.make(code.OpPop))),
        ("fn() {5+10}", (5, 10, code.Instructions(b''.join([code.make(code.OpConstant, 0),
                                        code.make(code.OpConstant, 1),
                                        code.make(code.OpAdd),
                                        code.make(code.OpReturnValue)]))),
         (code.make(code.OpConstant, 2), code.make(code.OpPop))),
        ("fn() {1;2}", (1, 2, code.Instructions(b''.join([code.make(code.OpConstant, 0),
                                        code.make(code.OpPop),
                                        code.make(code.OpConstant, 1),
                                        code.make(code.OpReturnValue)]))),
         (code.make(code.OpConstant, 2), code.make(code.OpPop))),
        ("fn() {}", (code.Instructions(b''.join([code.make(code.OpReturn)])),),
         (code.make(code.OpConstant, 0), code.make(code.OpPop))),
    ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True


def test_compiler_scopes():
    compiler = Compiler()
    if compiler.scope_index != 0:
        return f"scope_index wrong. got={compiler.scope_index}, want=0"
    global_st = compiler.symbol_table

    compiler.emit(code.OpMul)
    compiler.enter_scope()
    if compiler.scope_index != 1:
        return f"scope index wrong. got={compiler.scope_index} want=1"

    compiler.emit(code.OpSub)

    if len(compiler.scopes[compiler.scope_index].instructions) != 1:
        return f"instructions length wrong. got={len(compiler.scopes[compiler.scope_index].instructions)} want=1"
    last_instruction = compiler.scopes[compiler.scope_index].last_instruction
    if last_instruction.op_code != code.OpSub:
        return f"last_instruction.OpCode wrong. got={last_instruction.op_code} want={code.OpSub}"
    if compiler.symbol_table.outer != global_st:
        print("compiler did not enclose symbol table")

    compiler.leave_scope()
    if compiler.scope_index != 0:
        return f"scope index wrong. got={compiler.scope_index} want=0"
    if compiler.symbol_table != global_st:
        print("compiler did not restore global symbol table")
    compiler.emit(code.OpAdd)
    if len(compiler.scopes[compiler.scope_index].instructions) != 2:
        return f"instructions length wrong. got={len(compiler.scopes[compiler.scope_index].instructions)} want=2"

    last_instruction = compiler.scopes[compiler.scope_index].last_instruction
    if last_instruction.op_code != code.OpAdd:
        return f"last_instruction.OpCode wrong. got={last_instruction.op_code} want={code.OpAdd}"
    previous_instruction = compiler.scopes[compiler.scope_index].previous_instruction
    if previous_instruction.op_code != code.OpMul:
        return f"previous_instruction.OpCode wrong. got={previous_instruction.op_code} want={code.OpMul}"
    print('test_compiler_scopes pass')


def test_function_calls():
    cases = [
        ("fn() {24}();", (24, code.Instructions(b''.join([code.make(code.OpConstant, 0),
                                              code.make(code.OpReturnValue)])),),
         (code.make(code.OpConstant, 1),
          code.make(code.OpCall, 0),
          code.make(code.OpPop))),
        ("let noArg = fn() {24}; noArg();", (24, code.Instructions(b''.join([
                                              code.make(code.OpConstant, 0),
                                              code.make(code.OpReturnValue)])),),
         (code.make(code.OpConstant, 1),
          code.make(code.OpSetGlobal, 0),
          code.make(code.OpGetGlobal, 0),
          code.make(code.OpCall, 0),
          code.make(code.OpPop))),
        ("""
        let oneArg = fn(a) { a;};
            oneArg(24);
        """,
         (code.Instructions(b''.join([
             code.make(code.OpGetLocal, 0),
             code.make(code.OpReturnValue)])),24),
             (
              code.make(code.OpConstant, 0),
              code.make(code.OpSetGlobal, 0),
              code.make(code.OpGetGlobal, 0),
              code.make(code.OpConstant, 1),
              code.make(code.OpCall, 1),
              code.make(code.OpPop)
             )
         ),
        ("""
        let manyArg = fn(a, b, c) {a;b;c;};
            manyArg(24, 25, 26);
        """,
         (code.Instructions(b''.join([
             code.make(code.OpGetLocal, 0),
             code.make(code.OpPop),
             code.make(code.OpGetLocal, 1),
             code.make(code.OpPop),
             code.make(code.OpGetLocal, 2),
             code.make(code.OpReturnValue)
            ])),24, 25, 26),
             (
              code.make(code.OpConstant, 0),
              code.make(code.OpSetGlobal, 0),
              code.make(code.OpGetGlobal, 0),
              code.make(code.OpConstant, 1),
              code.make(code.OpConstant, 2),
              code.make(code.OpConstant, 3),
              code.make(code.OpCall, 3),
              code.make(code.OpPop)
             )
         ),

    ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True


def test_let_statement_scopes():
    cases = [
        ("""
        let num = 55;
        fn() { num }
        """,
        (55, code.Instructions(b''.join([code.make(code.OpGetGlobal, 0),
                                         code.make(code.OpReturnValue)])),),
        (code.make(code.OpConstant, 0),
         code.make(code.OpSetGlobal, 0),
         code.make(code.OpConstant, 1),
         code.make(code.OpPop))),
        ("""
        fn() {
                let num = 55;
                num
            }
        """,
        (55, code.Instructions(b''.join([
            code.make(code.OpConstant, 0),
            code.make(code.OpSetLocal, 0),
            code.make(code.OpGetLocal, 0),
            code.make(code.OpReturnValue)])),),
        (code.make(code.OpConstant, 1),
         code.make(code.OpPop))),
        ("""
        fn() {
                let a = 55;
                let b = 77;
                a+b
            }
        """,
        (55, 77,
         code.Instructions(b''.join([
            code.make(code.OpConstant, 0),
            code.make(code.OpSetLocal, 0),
            code.make(code.OpConstant, 1),
            code.make(code.OpSetLocal, 1),
            code.make(code.OpGetLocal, 0),
            code.make(code.OpGetLocal, 1),
            code.make(code.OpAdd),
            code.make(code.OpReturnValue)])),),
        (code.make(code.OpConstant, 2),
         code.make(code.OpPop))
         ),
    ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True

def test_builtins():
    cases = [
        ("""
        len([]);
        push([], 1);
        """,
         (1,),
         (code.make(code.OpGetBuiltin, 0),
         code.make(code.OpArray, 0),
         code.make(code.OpCall, 1),
         code.make(code.OpPop),
         code.make(code.OpGetBuiltin, 5),
         code.make(code.OpArray, 0),
         code.make(code.OpConstant, 0),
         code.make(code.OpCall, 2),
         code.make(code.OpPop),
         )),
        ("""
        fn() { len([]) }
        """,
         (code.Instructions(b''.join([
             code.make(code.OpGetBuiltin, 0),
             code.make(code.OpArray, 0),
             code.make(code.OpCall, 1),
             code.make(code.OpReturnValue),
            ])),
          ),
         (code.make(code.OpConstant, 0),
          code.make(code.OpPop)
          )
         ),
    ]
    err = run_compiler_tests(cases)
    if err is not None:
        return err
    return True

if __name__ == '__main__':
    test_compiler_scopes()
    tests = [
        test_integer_arithmetic,
        test_boolean_expressions,
        test_conditionals,
        test_global_let_statements,
        test_string_expressions,
        test_array_literals,
        test_hash_literals,
        test_index_expressions,
        test_functions,
        test_function_calls,
        test_let_statement_scopes,
        test_builtins
    ]
    test_util.run_cases(tests)


