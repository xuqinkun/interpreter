from dataclasses import dataclass

from monkey_code import code
from monkey_object import object

@dataclass
class Frame:
    fn: object.CompiledFunction
    ip: int

    def __init__(self, fn: object.CompiledFunction):
        self.fn = fn
        self.ip = -1

    def instructions(self) -> code.Instructions:
        return self.fn.instructions
