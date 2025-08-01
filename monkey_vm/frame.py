from dataclasses import dataclass

from monkey_code import code
from monkey_object import object

@dataclass
class Frame:
    cl: object.Closure
    ip: int
    base_pointer: int

    def __init__(self, cl: object.Closure, base_pointer: int):
        self.cl = cl
        self.ip = -1
        self.base_pointer = base_pointer

    def instructions(self) -> code.Instructions:
        return self.cl.fn.instructions
