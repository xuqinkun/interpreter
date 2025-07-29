from dataclasses import dataclass

from monkey_code import code
from monkey_object import object

@dataclass
class Frame:
    fn: object.CompiledFunction
    ip: int
    base_pointer: int

    def __init__(self, fn: object.CompiledFunction, base_pointer: int):
        self.fn = fn
        self.ip = -1
        self.base_pointer = base_pointer

    def instructions(self) -> code.Instructions:
        return self.fn.instructions
