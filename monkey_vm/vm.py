from dataclasses import dataclass
from typing import List, cast
from monkey_code import code
from monkey_compiler import compiler
from monkey_object import object

STACK_SIZE=2048

@dataclass
class VM:
    constants: List[object.Object]
    instructions: code.Instructions
    stack: List[object.Object]
    sp: int

    @staticmethod
    def new(bytecode: compiler.Bytecode):
        stack = cast(List[object.Object], [None] * STACK_SIZE)
        return VM(instructions=bytecode.instructions,
                  constants=bytecode.constants,
                  stack=stack,
                  sp=0)

    def peek(self):
        if self.sp == 0:
            return None
        return self.stack[self.sp - 1]

    def run(self):
        ip = 0
        while ip < len(self.instructions):
            op = code.Opcode(self.instructions[ip])
            if op == code.OpConstant:
                const_index = code.read_uint16(self.instructions[ip+1:])
                ip += 2
                err = self.push(self.constants[const_index])
                if err is not None:
                    return err
            elif op in [code.OpAdd, code.OpSub, code.OpMul, code.OpDiv]:
                right = self.pop()
                left = self.pop()
                left_val = left.value
                right_val = right.value
                left_type = left.type()
                right_type = right.type()
                if left_type == object.INTEGER_OBJ and right_type == object.INTEGER_OBJ:
                    if op == code.OpAdd:
                        result = left_val + right_val
                    elif op == code.OpSub:
                        result = left_val - right_val
                    elif op == code.OpMul:
                        result = left_val * right_val
                    else:
                        result = left_val / right_val
                    self.push(object.Integer(result))
            elif op == code.OpPop:
                self.pop()
            else:
                return f"unknown operator: {op}"
            ip += 1
        return None

    def push(self, obj: object.Object):
        if self.sp >= STACK_SIZE:
            return f"Stack Overflow"
        self.stack[self.sp] = obj
        self.sp += 1
        return None

    def pop(self):
        o = self.stack[self.sp - 1]
        self.sp -= 1
        return o

    def last_popped_stack_elem(self):
        return self.stack[self.sp]