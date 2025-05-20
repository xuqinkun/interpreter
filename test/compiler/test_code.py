from monkey_code import code
from util import test_util

def test_instructions_string():
    instructions = [
        code.make(code.OpConstant, 1),
        code.make(code.OpConstant, 2),
        code.make(code.OpConstant, 65535),
    ]
    expected  = """
        0000 OpConstant 1
        0003 OpConstant 2
        0006 OpConstant 65535
    """
    concat = b''.join(instructions)

    if str(concat) != expected:
        return f"instructions wrongly formatted. \nwant={expected} got={concat}"
    return None


def test_read_operands():
    cases = [
        (code.OpConstant, [65535], 2)
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
        test_read_operands,
        test_instructions_string,
    ]
    test_util.run_cases(tests)