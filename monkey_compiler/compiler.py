from dataclasses import dataclass
from typing import List
from monkey_ast import ast
from monkey_code import code
from monkey_object import object


@dataclass()
class Bytecode:
    instructions: code.Instructions=b''
    constants: List[object.Object]=None

@dataclass()
class Compiler:
    instructions: code.Instructions=b''
    constants: List[object.Object]=None


    def compile(self, program: ast.Program):
        return None

    def bytecode(self):
        return Bytecode(self.instructions, self.constants)
