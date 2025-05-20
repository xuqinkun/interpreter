from dataclasses import dataclass
from enum import Enum, auto
from typing import List, Dict, Optional, Tuple
import struct

Instructions = List[bytes]  # or List[bytes] if you specifically want bytes

Opcode = int  # or use 'bytes' if you specifically want a single byte

OpConstant = 1

@dataclass
class Definition:
    name: str
    operand_widths: List[int]


definitions: Dict[Opcode, Definition] = {
    OpConstant: Definition(name="OpConstant", operand_widths=[2]),
}


def lookup(op: Opcode) -> Tuple[Optional[Definition], Optional[str]]:
    define = definitions.get(op, None)
    if define is None:
        return define, f"opcode {op} undefined"
    else:
        return define, None



def make(op: int, operands: List[int]) -> bytes:
    define = definitions.get(op, None)
    if define is None:
        return b''
    ins_len = 1 + sum(define.operand_widths)
    instruction = bytearray(ins_len)
    instruction[0] = op
    offset = 1
    for operand, width in zip(operands, define.operand_widths):
        if width == 2:
            # 以大端序写入2字节无符号整数
            struct.pack_into('>H', instruction, offset, operand)
        offset += width
    return bytes(instruction)




if __name__ == '__main__':
    if make(1, 0):
        print('ok')
    else:
        print('empty')