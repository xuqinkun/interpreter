from dataclasses import dataclass
from typing import List

from monkey_ast import ast
from monkey_code import code
from monkey_object import object


@dataclass()
class Bytecode:
    instructions: code.Instructions = b''
    constants: List[object.Object] = None


@dataclass()
class Compiler:
    instructions: code.Instructions = b''
    constants: List[object.Object] = None

    def __init__(self):
        self.instructions = code.Instructions()
        self.constants = []

    def compile(self, node: ast.Node):
        if isinstance(node, ast.Program):
            for s in node.statements:
                err = self.compile(s)
                if err is not None:
                    return err
        elif isinstance(node, ast.ExpressionStatement):
            err = self.compile(node.expression)
            if err is not None:
                return err
            self.emit(code.OpPop)
        elif isinstance(node, ast.InfixExpression):
            err = self.compile(node.left)
            if err is not None:
                return err
            err = self.compile(node.right)
            if err is not None:
                return err
            if node.operator == '+':
                self.emit(code.OpAdd)
            elif node.operator == '-':
                self.emit(code.OpSub)
            elif node.operator == '*':
                self.emit(code.OpMul)
            elif node.operator == '/':
                self.emit(code.OpDiv)
            else:
                return f"unknown operator {node.operator}"
        elif isinstance(node, ast.IntegerLiteral):
            integer = object.Integer(node.value)
            pos = self.add_constant(integer)
            self.emit(code.OpConstant, pos)
        return None

    def add_constant(self, obj: object.Object):
        self.constants.append(obj)
        return len(self.constants) - 1

    def emit(self, op: int, *operands) -> int:
        if operands is None:
            operands = []
        ins = code.make(op, *operands)
        pos = self.add_instruction(ins)
        return pos

    def add_instruction(self, ins: bytes) -> int:
        pos_new_instruction = len(self.instructions)
        self.instructions += ins
        return pos_new_instruction

    def bytecode(self):
        return Bytecode(self.instructions, self.constants)
