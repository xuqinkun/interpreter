import struct
from dataclasses import dataclass
from io import StringIO
from typing import List, Dict, Optional, Tuple

Opcode = int  # or use 'bytes' if you specifically want a single byte

OpConstant = 1


@dataclass
class Definition:
    name: str
    operand_widths: List[int]


class Instructions(bytes):

    def string(self):
        out = StringIO()
        i = 0
        while i < len(self):
            define, err = lookup(self[i])
            if err is not None:
                out.write(f"ERROR: {err}\n")
                continue
            operands, n_bytes = read_operands(define, self[i + 1:])
            out.write(f"{i:04d} {self.format(define, operands)}\n")
            i += 1 + n_bytes
        return out.getvalue()

    def format(self, define: Definition, operands: List[int]):
        operand_count = len(define.operand_widths)
        if len(operands) != operand_count:
            return f"ERROR: operand len {len(operands)} does not match defined {operand_count}\n"
        if operand_count == 1:
            return f"{define.name} {operands[0]}"
        return f"ERROR: unhandled operand_count for {define.name}\n"


definitions: Dict[Opcode, Definition] = {
    OpConstant: Definition(name="OpConstant", operand_widths=[2]),
}


def lookup(op: Opcode) -> Tuple[Optional[Definition], Optional[str]]:
    define = definitions.get(op, None)
    if define is None:
        return define, f"opcode {op} undefined"
    else:
        return define, None


def make(op: int, *operands) -> Instructions:
    define = definitions.get(op, None)
    if define is None:
        return Instructions(b'')
    ins_len = 1 + sum(define.operand_widths)
    instruction = bytearray(ins_len)
    instruction[0] = op
    offset = 1
    for operand, width in zip(operands, define.operand_widths):
        if width == 2:
            # 以大端序写入2字节无符号整数
            struct.pack_into('>H', instruction, offset, operand)
        offset += width
    return Instructions(instruction)


def read_operands(define: Definition, ins: bytes):
    operands = [0] * len(define.operand_widths)
    offset = 0
    for i, width in enumerate(define.operand_widths):
        if width == 2:
            operands[i] = read_uint16(ins[offset:offset + 2])
        offset += width
    return operands, offset


def read_uint16(ins: bytes) -> int:
    """Read 2 bytes as big-endian unsigned short (0-65535)"""
    return struct.unpack('>H', ins[:2])[0]
