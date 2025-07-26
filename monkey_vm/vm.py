from dataclasses import dataclass
from typing import List, cast

from monkey_code import code
from monkey_compiler import compiler
from monkey_object import object

STACK_SIZE = 2048
GLOBAL_SIZE = 65536
TRUE = object.Boolean(True)
FALSE = object.Boolean(False)
NULL = object.Null()


@dataclass
class VM:
    constants: List[object.Object]
    instructions: code.Instructions
    stack: List[object.Object]
    sp: int
    globals: List[object.Object]

    @staticmethod
    def new(bytecode: compiler.Bytecode):
        stack = cast(List[object.Object], [None] * STACK_SIZE)
        globals = cast(List[object.Object], [None] * GLOBAL_SIZE)
        return VM(instructions=bytecode.instructions,
                  constants=bytecode.constants,
                  stack=stack,
                  sp=0,
                  globals=globals)

    @staticmethod
    def new_with_global_state(bytecode: compiler.Bytecode, s: List[object.Object]):
        vm = VM.new(bytecode)
        vm.globals = s
        return vm

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
                const_index = code.read_uint16(self.instructions[ip + 1:])
                ip += 2
                err = self.push(self.constants[const_index])
                if err is not None:
                    return err
            elif op in [code.OpAdd, code.OpSub, code.OpMul, code.OpDiv]:
                err = self.execute_binary_operation(op)
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
            elif op == code.OpBang:
                err = self.execute_bang_operator()
                if err is not None:
                    return err
            elif op == code.OpMinus:
                err = self.execute_minus_operator()
                if err is not None:
                    return err
            elif op in [code.OpEqual, code.OpNotEqual, code.OpGreaterThan]:
                err = self.execute_comparison(op)
                if err is not None:
                    return err
            elif op == code.OpJump:
                pos = code.read_uint16(self.instructions[ip + 1:])
                ip = pos - 1
            elif op == code.OpJumpNotTruthy:
                pos = code.read_uint16(self.instructions[ip + 1:])
                ip += 2
                condition = self.pop()
                if not is_truthy(condition):
                    ip = pos - 1
            elif op == code.OpNull:
                err = self.push(NULL)
                if err is not None:
                    return err
            elif op == code.OpSetGlobal:
                global_index = code.read_uint16(self.instructions[ip + 1:])
                ip += 2
                self.globals[global_index] = self.pop()
            elif op == code.OpGetGlobal:
                global_index = code.read_uint16(self.instructions[ip + 1:])
                ip += 2
                err = self.push(self.globals[global_index])
                if err is not None:
                    return err
            elif op == code.OpArray:
                num_elements = int(code.read_uint16(self.instructions[ip + 1:]))
                ip += 2
                array = self.build_array(self.sp - num_elements, self.sp)
                err = self.push(array)
                if err is not None:
                    return err
            elif op == code.OpHash:
                num_elements = int(code.read_uint16(self.instructions[ip + 1:]))
                ip += 2
                hash_obj, err = self.build_hash(self.sp - num_elements, self.sp)
                if err is not None:
                    return err
                self.sp = self.sp - num_elements
                err = self.push(hash_obj)
                if err is not None:
                    return err
            elif op == code.OpIndex:
                index = self.pop()
                left = self.pop()
                err = self.execute_index_expression(left, index)
                if err is not None:
                    return err
            else:
                return f"unknown operator: {definition.name}"
            ip += 1
        return None

    def build_array(self, start_idx, end_idx):
        return object.Array(self.stack[start_idx: end_idx])

    def execute_index_expression(self, left: object.Object, index: object.Object):
        if left.type() == object.ARRAY_OBJ and index.type() == object.INTEGER_OBJ:
            return self.execute_array_index(left, index)
        elif left.type() == object.HASH_OBJ:
            return self.execute_hash_index(left, index)
        return f"index operator not supported: {left.type()}"

    def execute_array_index(self, array: object.Array, index: object.Integer):
        pos = index.value
        size = len(array.elements)
        if pos < 0 or pos >= size:
            return self.push(NULL)
        return self.push(array.elements[pos])

    def execute_hash_index(self, hash_pairs: object.Hash, index: object.Hashable):
        if not isinstance(index, object.Hashable):
            return f"unhashable key {index.type()}"
        if index.hash_key() not in hash_pairs.pairs:
            return self.push(NULL)
        pair = hash_pairs.pairs[index.hash_key()]
        return self.push(pair.value)

    def build_hash(self, start_idx, end_idx):
        hashed_pairs = {}
        for i in range(start_idx, end_idx, 2):
            key = self.stack[i]
            value = self.stack[i + 1]
            pair = object.HashPair(key=key, value=value)
            if not isinstance(key, object.Hashable):
                return f"unhashable key {key.type()}"
            hashed_pairs[key.hash_key()] = pair
        return object.Hash(pairs=hashed_pairs), None

    def execute_binary_operation(self, op: code.Opcode):
        right = self.pop()
        left = self.pop()
        left_type = left.type()
        right_type = right.type()
        if left_type == object.INTEGER_OBJ and right_type == object.INTEGER_OBJ:
            return self.execute_binary_integer_operation(op, left, right)
        elif left_type == object.STRING_OBJ and right_type == object.STRING_OBJ:
            return self.execute_binary_string_operation(op, left, right)
        return f"unsupported types for binary operation: {left_type} {right_type}"

    def execute_binary_string_operation(self, op: code.Opcode, left: object.Object, right: object.Object):
        if op != code.OpAdd:
            return f"unknown string operator: {op}"
        left_value = left.value
        right_value = right.value
        return self.push(object.String(left_value + right_value))

    def execute_binary_integer_operation(self, op: code.Opcode, left: object.Object, right: object.Object):
        left_value = left.value
        right_val = right.value
        if op == code.OpAdd:
            result = left_value + right_val
        elif op == code.OpSub:
            result = left_value - right_val
        elif op == code.OpMul:
            result = left_value * right_val
        else:
            result = left_value / right_val
        return self.push(object.Integer(result))

    def execute_comparison(self, op: code.Opcode):
        right = self.pop()
        left = self.pop()
        if left.type() == object.INTEGER_OBJ and right.type() == object.INTEGER_OBJ:
            return self.execute_integer_comparison(op, left, right)
        if op == code.OpEqual:
            return self.push(native_bool_to_boolean_object(right == left))
        elif op == code.OpNotEqual:
            return self.push(native_bool_to_boolean_object(right != left))
        else:
            return f"unknown error: {op} {left.type()} {right.type()}"

    def execute_integer_comparison(self, op: code.Opcode, left: object.Object, right: object.Object):
        left_val = left.value
        right_val = right.value
        if op == code.OpEqual:
            return self.push(native_bool_to_boolean_object(left_val == right_val))
        elif op == code.OpNotEqual:
            return self.push(native_bool_to_boolean_object(left_val != right_val))
        elif op == code.OpGreaterThan:
            return self.push(native_bool_to_boolean_object(left_val > right_val))
        else:
            return f"unknown operator {op}"

    def execute_bang_operator(self):
        operand = self.pop()
        if operand == TRUE:
            return self.push(FALSE)
        elif operand == FALSE:
            return self.push(TRUE)
        elif operand == NULL:
            return self.push(TRUE)
        else:
            return self.push(FALSE)

    def execute_minus_operator(self):
        operand = self.pop()
        if operand.type() != object.INTEGER_OBJ:
            return f"unsupported type for negation: {operand.type()}"
        value = operand.value
        return self.push(object.Integer(-value))

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


def is_truthy(obj: object.Object):
    if isinstance(obj, object.Boolean):
        return obj.value
    elif isinstance(obj, object.Null):
        return False
    return True
