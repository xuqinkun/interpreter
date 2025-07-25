from dataclasses import dataclass
from typing import List

from monkey_ast import ast
from monkey_code import code
from monkey_compiler.symbol_table import SymbolTable
from monkey_object import object


@dataclass()
class Bytecode:
    instructions: code.Instructions = b''
    constants: List[object.Object] = None


@dataclass()
class EmittedInstruction:
    op_code: code.Opcode = 0
    pos: int = 0


@dataclass()
class Compiler:
    instructions: code.Instructions = b''
    constants: List[object.Object] = None
    last_instruction: EmittedInstruction = None
    previous_instruction: EmittedInstruction = None
    symbol_table: SymbolTable = None

    def __init__(self):
        self.instructions = code.Instructions()
        self.constants = []
        self.last_instruction = EmittedInstruction()
        self.previous_instruction = EmittedInstruction()
        self.symbol_table = SymbolTable()

    @staticmethod
    def new_with_state(s: SymbolTable, constants: List[object.Object]):
        compiler = Compiler()
        compiler.symbol_table = s
        compiler.constants = constants
        return compiler

    def compile(self, node: ast.Node):
        if isinstance(node, ast.Program):
            for s in node.statements:
                err = self.compile(s)
                if err is not None:
                    return err
        elif isinstance(node, ast.Boolean):
            if node.value:
                self.emit(code.OpTrue)
            else:
                self.emit(code.OpFalse)
        elif isinstance(node, ast.ExpressionStatement):
            err = self.compile(node.expression)
            if err is not None:
                return err
            self.emit(code.OpPop)
        elif isinstance(node, ast.PrefixExpression):
            err = self.compile(node.right)
            if err is not None:
                return err
            if node.operator == '!':
                self.emit(code.OpBang)
            elif node.operator == '-':
                self.emit(code.OpMinus)
            else:
                return f"unknown operator {node.operator}"
        elif isinstance(node, ast.InfixExpression):
            if node.operator == '<':
                err = self.compile(node.right)
                if err is not None:
                    return err
                err = self.compile(node.left)
                if err is not None:
                    return err
                self.emit(code.OpGreaterThan)
                return None
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
            elif node.operator == '>':
                self.emit(code.OpGreaterThan)
            elif node.operator == '==':
                self.emit(code.OpEqual)
            elif node.operator == '!=':
                self.emit(code.OpNotEqual)
            else:
                return f"unknown operator {node.operator}"
        elif isinstance(node, ast.IFExpression):
            err = self.compile(node.condition)
            if err is not None:
                return err
            jump_not_truthy_pos = self.emit(code.OpJumpNotTruthy, 9999)
            err = self.compile(node.consequence)
            if err is not None:
                return err
            if self.last_instruction_is_pop():
                self.remove_last_pop()

            jump_pos = self.emit(code.OpJump, 9999)

            after_consequence_pos = len(self.instructions)
            self.change_operand(jump_not_truthy_pos, after_consequence_pos)
            if node.alternative is None:
                self.emit(code.OpNull)
            else:
                err = self.compile(node.alternative)
                if err is not None:
                    return err
                if self.last_instruction_is_pop():
                    self.remove_last_pop()
            after_consequence_pos = len(self.instructions)
            self.change_operand(jump_pos, after_consequence_pos)
        elif isinstance(node, ast.IntegerLiteral):
            integer = object.Integer(node.value)
            pos = self.add_constant(integer)
            self.emit(code.OpConstant, pos)
        elif isinstance(node, ast.BlockStatement):
            for s in node.statements:
                err = self.compile(s)
                if err is not None:
                    return err
        elif isinstance(node, ast.LetStatement):
            err = self.compile(node.value)
            if err is not None:
                return err
            symbol = self.symbol_table.define(node.name.value)
            self.emit(code.OpSetGlobal, symbol.index)
        elif isinstance(node, ast.Identifier):
            symbol, ok = self.symbol_table.resolve(node.value)
            if not ok:
                return f"undefined variable: {node.value}"
            self.emit(code.OpGetGlobal, symbol.index)
        return None

    def last_instruction_is_pop(self):
        return self.last_instruction.op_code == code.OpPop

    def remove_last_pop(self):
        self.instructions = code.Instructions(self.instructions[:self.last_instruction.pos])
        self.last_instruction = self.previous_instruction

    def add_constant(self, obj: object.Object):
        self.constants.append(obj)
        return len(self.constants) - 1

    def emit(self, op: int, *operands) -> int:
        if operands is None:
            operands = []
        ins = code.make(op, *operands)
        pos = self.add_instruction(ins)
        self.set_last_instruction(op, pos)
        return pos

    def replace_instructions(self, pos: int, new_instruction: code.Instructions):

        for i in range(len(new_instruction)):
            self.instructions[pos+i] = new_instruction[i]

    def set_last_instruction(self, op: code.Opcode, pos: int):
        previous = self.last_instruction
        last = EmittedInstruction(op_code=op, pos=pos)
        self.previous_instruction = previous
        self.last_instruction = last

    def add_instruction(self, ins: code.Instructions) -> int:
        pos_new_instruction = len(self.instructions)
        self.instructions += ins
        return pos_new_instruction


    def change_operand(self, op_pos: int, operand: int):
        op = code.Opcode(self.instructions[op_pos])
        new_instruction = code.make(op, operand)
        self.replace_instructions(op_pos, new_instruction)

    def bytecode(self):
        return Bytecode(self.instructions, self.constants)
