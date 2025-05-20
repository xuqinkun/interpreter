from monkey_code.code import *
from util.test_util import run_cases

def test_name():
    cases = [
        (OpConstant, [65534],
        [OpConstant, 255, 254])
    ]
    for (op, operands, expected) in cases:
        instruction = make(op, operands)
        if len(instruction) != len(expected):
            return False, f"instruction has wrong length. want={len(expected)}, got={len(instruction)}"
        for i, exp in enumerate(expected):
            if instruction[i] != exp:
                return False, f"wrong byte at pos {i}. want={exp}, got={instruction[i]}"
        return True



if __name__ == '__main__':
    cases = [
        test_name
    ]
    run_cases(cases)