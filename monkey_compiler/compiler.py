from typing import List

from monkey_ast import ast
from monkey_code import code
from monkey_compiler.symbol_table import *
from monkey_object import builtins
from monkey_object import object


@dataclass()
class Bytecode:
    instructions: code.Instructions = b''
    constants: List[object.Object] = None

    def __init__(self, instructions: code.Instructions, constants: List[object.Object]):
        self.instructions = instructions
        self.constants = constants


@dataclass()
class EmittedInstruction:
    op_code: code.Opcode = 0
    pos: int = 0

    def __init__(self, op_code: code.Opcode, pos: int):
        self.op_code = op_code
        self.pos = pos


@dataclass()
class CompilationScope:
    instructions: code.Instructions
    last_instruction: EmittedInstruction
    previous_instruction: EmittedInstruction

    def __init__(self, instructions: code.Instructions, last_instruction: EmittedInstruction,
                 previous_instruction: EmittedInstruction):
        self.instructions = instructions
        self.last_instruction = last_instruction
        self.previous_instruction = previous_instruction

@dataclass()
class Compiler:
    instructions: code.Instructions = b''
    constants: List[object.Object] = None
    last_instruction: EmittedInstruction = None
    previous_instruction: EmittedInstruction = None
    symbol_table: SymbolTable = None
    scopes: List[CompilationScope] = None
    scope_index: int = 0

    def __init__(self):
        self.instructions = code.Instructions()
        self.constants = []
        self.last_instruction = EmittedInstruction(op_code=0, pos=0)
        self.previous_instruction = EmittedInstruction(op_code=0, pos=0)
        self.symbol_table = SymbolTable()
        for i, fn in enumerate(builtins.builtins):
            self.symbol_table.define_builtin(i, fn[0])
        scope = CompilationScope(instructions=code.Instructions(),
                         last_instruction=EmittedInstruction(op_code=0, pos=0),
                         previous_instruction=EmittedInstruction(op_code=0, pos=0))
        self.scopes = [scope]
        self.scope_index = 0

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
            if self.last_instruction_is(code.OpPop):
                self.remove_last_pop()

            jump_pos = self.emit(code.OpJump, 9999)

            after_consequence_pos = len(self.current_instructions())
            self.change_operand(jump_not_truthy_pos, after_consequence_pos)
            if node.alternative is None:
                self.emit(code.OpNull)
            else:
                err = self.compile(node.alternative)
                if err is not None:
                    return err
                if self.last_instruction_is(code.OpPop):
                    self.remove_last_pop()
            after_alternative_pos = len(self.current_instructions())
            self.change_operand(jump_pos, after_alternative_pos)
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
            if symbol.scope == GlobalScope:
                self.emit(code.OpSetGlobal, symbol.index)
            else:
                self.emit(code.OpSetLocal, symbol.index)
        elif isinstance(node, ast.Identifier):
            symbol, ok = self.symbol_table.resolve(node.value)
            if not ok:
                return f"undefined variable: {node.value}"
            if symbol.scope == GlobalScope:
                self.emit(code.OpGetGlobal, symbol.index)
            elif symbol.scope == LocalScope:
                self.emit(code.OpGetLocal, symbol.index)
            elif symbol.scope == BuiltinScope:
                self.emit(code.OpGetBuiltin, symbol.index)
        elif isinstance(node, ast.StringLiteral):
            s = object.String(node.value)
            self.emit(code.OpConstant, self.add_constant(s))
        elif isinstance(node, ast.ArrayLiteral):
            for i, el in enumerate(node.elements):
                err = self.compile(el)
                if err is not None:
                    return err
            self.emit(code.OpArray, len(node.elements))
        elif isinstance(node, ast.HashLiteral):
            keys = list(node.pairs.keys())
            keys.sort(key=lambda x: str(x))
            for key in keys:
                err = self.compile(key)
                if err is not None:
                    return err
                err = self.compile(node.pairs[key])
                if err is not None:
                    return err
            self.emit(code.OpHash, len(node.pairs) * 2)
        elif isinstance(node, ast.IndexExpression):
            err = self.compile(node.left)
            if err is not None:
                return err
            err = self.compile(node.index)
            if err is not None:
                return err
            self.emit(code.OpIndex)
        elif isinstance(node, ast.FunctionLiteral):
            self.enter_scope()
            for p in node.parameters:
                self.symbol_table.define(p.value)
            err = self.compile(node.body)
            if err is not None:
                return err
            if self.last_instruction_is(code.OpPop):
                self.replace_last_pop_with_return()
            if not self.last_instruction_is(code.OpReturnValue):
                self.emit(code.OpReturn)
            num_locals = self.symbol_table.num_definitions
            instructions = self.leave_scope()
            compiled_function = object.CompiledFunction(
                instructions=instructions,
                num_locals=num_locals,
                num_parameters=len(node.parameters)
            )
            self.emit(code.OpConstant, self.add_constant(compiled_function))
        elif isinstance(node, ast.ReturnStatement):
            err = self.compile(node.return_value)
            if err is not None:
                return err
            self.emit(code.OpReturnValue)
        elif isinstance(node, ast.CallExpression):
            err = self.compile(node.function)
            if err is not None:
                return err
            for a in node.arguments:
                err = self.compile(a)
                if err is not None:
                    return err
            self.emit(code.OpCall, len(node.arguments))
        return None

    def last_instruction_is(self, op: code.Opcode):
        if len(self.current_instructions()) == 0:
            return False
        return self.scopes[self.scope_index].last_instruction.op_code == op

    def replace_last_pop_with_return(self):
        last_pos = self.scopes[self.scope_index].last_instruction.pos
        self.replace_instructions(last_pos, code.make(code.OpReturnValue))
        self.scopes[self.scope_index].last_instruction.op_code = code.OpReturnValue

    def remove_last_pop(self):
        last = self.scopes[self.scope_index].last_instruction
        previous = self.scopes[self.scope_index].previous_instruction
        old = self.current_instructions()
        new = old[:last.pos]
        self.scopes[self.scope_index].instructions = new
        self.scopes[self.scope_index].last_instruction = previous

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
        ins = self.current_instructions()
        for i in range(len(new_instruction)):
            ins[pos+i] = new_instruction[i]

    def set_last_instruction(self, op: code.Opcode, pos: int):
        previous = self.scopes[self.scope_index].last_instruction
        last = EmittedInstruction(op_code=op, pos=pos)
        self.scopes[self.scope_index].previous_instruction = previous
        self.scopes[self.scope_index].last_instruction = last

    def add_instruction(self, ins: code.Instructions) -> int:
        pos_new_instruction = len(self.current_instructions())
        self.scopes[self.scope_index].instructions += ins
        return pos_new_instruction

    def change_operand(self, op_pos: int, operand: int):
        op = code.Opcode(self.current_instructions()[op_pos])
        new_instruction = code.make(op, operand)
        self.replace_instructions(op_pos, new_instruction)

    def bytecode(self):
        return Bytecode(self.current_instructions(), self.constants)

    def current_instructions(self):
        return self.scopes[self.scope_index].instructions

    def enter_scope(self):
        scope = CompilationScope(instructions=code.Instructions(),
                                 last_instruction=EmittedInstruction(op_code=0, pos=0),
                                 previous_instruction=EmittedInstruction(op_code=0, pos=0))
        self.symbol_table = SymbolTable.new_enclosed(self.symbol_table)
        self.scopes.append(scope)
        self.scope_index += 1

    def leave_scope(self):
        self.symbol_table = self.symbol_table.outer
        instructions = self.current_instructions()
        self.scopes = self.scopes[: len(self.scopes) - 1]
        self.scope_index -= 1
        return instructions