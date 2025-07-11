from dataclasses import dataclass
from typing import List, cast
from monkey_code import code
from monkey_compiler import compiler
from monkey_object import object

STACK_SIZE=2048
TRUE = object.Boolean(True)
FALSE = object.Boolean(False)

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
            definition, ok = code.lookup(op)
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
                    err = self.push(object.Integer(result))
                    if err is not None:
                        return err
            elif op == code.OpPop:
                self.pop()
            elif op == code.OpTrue:
                err = self.push(TRUE)
                if err is not None:
                    return err
            elif op == code.OpFalse:
                err = self.push(FALSE)
                if err is not None:
                    return err
            elif op in [code.OpEqual, code.OpNotEqual, code.OpGreaterThan]:
                err = self.execute_comparison(op)
                if err is not None:
                    return err
            else:
                return f"unknown operator: {definition.name}"
            ip += 1
        return None

    def execute_integer_comparison(self, op: code.Opcode, left: object.Object, right: object.Object):
        left_val = left.value
        right_val = right.value
        if op == code.OpEqual:
            return self.push(native_bool_to_boolean_object(left_val == right_val))
        elif op == code.OpNotEqual:
            return self.push(native_bool_to_boolean_object(left_val != right_val))
        elif op == code.OpGreaterThan:
            return self.push(native_bool_to_boolean_object(left_val > right_val))
        return f"unknown operator: {op}"


    def execute_comparison(self, op: code.Opcode):
        right = self.pop()
        left = self.pop()
        left_type = left.type()
        right_type = right.type()
        if left_type == object.INTEGER_OBJ and right_type == object.INTEGER_OBJ:
            return self.execute_integer_comparison(op, left, right)
        if op == code.OpEqual:
            return self.push(native_bool_to_boolean_object(right == left))
        elif op == code.OpNotEqual:
            return self.push(native_bool_to_boolean_object(right != left))
        else:
            return f"unknown operator: {op} {left_type} {right_type}"


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


def native_bool_to_boolean_object(condition: bool):
    if condition:
        return TRUE
    else:
        return FALSE