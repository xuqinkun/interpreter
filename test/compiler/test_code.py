from monkey_code.code import *
from monkey_code import code
from util import test_util

def test_make():
    cases = [
        (OpConstant, [65534], [OpConstant, 255, 254]),
        (OpAdd, [], [OpAdd]),
        (OpGetLocal, [255], [OpGetLocal, 255]),
        (OpClosure, [65534, 255], [OpClosure, 255, 254, 255]),
    ]
    for (op, operands, expected) in cases:
        instruction = make(op, *operands)
        if len(instruction) != len(expected):
            return False, f"instruction has wrong length. want={len(expected)}, got={len(instruction)}"
        for i, exp in enumerate(expected):
            if instruction[i] != exp:
                return False, f"wrong byte at pos {i}. want={exp}, got={instruction[i]}"
    return True


def test_instructions_string():
    instructions = [
        code.make(code.OpAdd),
        code.make(code.OpGetLocal, 1),
        code.make(code.OpConstant, 2),
        code.make(code.OpConstant, 65535),
        code.make(code.OpClosure, 65535, 255),
    ]
    expected  = "0000 OpAdd\n0001 OpGetLocal 1\n0003 OpConstant 2\n0006 OpConstant 65535\n0009 OpClosure 65535 255\n"

    concatenated = code.Instructions(b''.join(instructions))
    if str(concatenated) != expected:
        return False, f"instructions wrongly formatted. \nwant={expected} got={concatenated}"
    return None


def test_read_operands():
    cases = [
        (code.OpConstant, [65535], 2),
        (code.OpGetLocal, [255], 1),
        (code.OpClosure, [65535, 255], 3),
    ]
    for op, operands, read_bytes in cases:
        ins = code.make(op, *operands)
        define, err = code.lookup(op)
        if err is not None:
            return f"definition not found: {err}"
        operands_read, n = code.read_operands(define, ins[1:])
        if n != read_bytes:
            return f"n wrong. want={read_bytes} got={n}"
        for actual, want in zip(operands_read, operands):
            if actual != want:
                return f"operand wrong. want={want} got={actual}"
    return True


if __name__ == '__main__':
    tests = [
        test_make,
        test_read_operands,
        test_instructions_string,
    ]
    test_util.run_cases(tests)