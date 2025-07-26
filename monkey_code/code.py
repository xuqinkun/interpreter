import struct
from dataclasses import dataclass
from io import StringIO
from typing import List, Dict, Optional, Tuple

Opcode = int  # or use 'bytes' if you specifically want a single byte

OpConstant = 1
OpAdd = 2
OpPop = 3
OpSub = 4
OpMul = 5
OpDiv = 6
OpTrue = 7
OpFalse = 8
OpEqual = 9
OpNotEqual = 10
OpGreaterThan = 11
OpMinus = 12
OpBang = 13
OpJump = 14
OpJumpNotTruthy = 15
OpNull = 16
OpGetGlobal = 17
OpSetGlobal = 18
OpArray = 19
OpHash = 20
OpIndex = 21


@dataclass
class Definition:
    name: str
    operand_widths: List[int]

definitions: Dict[Opcode, Definition] = {
    OpConstant: Definition(name="OpConstant", operand_widths=[2]),
    OpAdd: Definition(name="OpAdd", operand_widths=[]),
    OpPop: Definition(name="OpPop", operand_widths=[]),
    OpSub: Definition(name="OpSub", operand_widths=[]),
    OpMul: Definition(name="OpMul", operand_widths=[]),
    OpDiv: Definition(name="OpDiv", operand_widths=[]),
    OpTrue: Definition(name="OpTrue", operand_widths=[]),
    OpFalse: Definition(name="OpFalse", operand_widths=[]),
    OpEqual: Definition(name="OpEqual", operand_widths=[]),
    OpNotEqual: Definition(name="OpNotEqual", operand_widths=[]),
    OpGreaterThan: Definition(name="OpGreaterThan", operand_widths=[]),
    OpMinus: Definition(name="OpMinus", operand_widths=[]),
    OpBang: Definition(name="OpBang", operand_widths=[]),
    OpJump: Definition(name="OpJump", operand_widths=[2]),
    OpJumpNotTruthy: Definition(name="OpJumpNotTruthy", operand_widths=[2]),
    OpNull: Definition(name="OpNull", operand_widths=[]),
    OpGetGlobal: Definition(name="OpGetGlobal", operand_widths=[2]),
    OpSetGlobal: Definition(name="OpSetGlobal", operand_widths=[2]),
    OpArray: Definition(name="OpArray", operand_widths=[2]),
    OpHash: Definition(name="OpHash", operand_widths=[2]),
    OpIndex: Definition(name="OpIndex", operand_widths=[]),
}

@dataclass
class Definition:
    name: str
    operand_widths: List[int]


class Instructions(bytearray):

    def __str__(self):
        out = StringIO()
        i = 0
        while i < len(self):
            define, err = lookup(self[i])
            if err is not None:
                out.write(f"ERROR: {err}\n")
                continue
            operands, n_bytes = read_operands(define, self[i + 1:])
            out.write(f"{i:04d} {self.format(define, operands)}\n")
            i += (1 + n_bytes)
        return out.getvalue()

    def __repr__(self):
        return self.__str__()

    def format(self, define: Definition, operands: List[int]):
        operand_count = len(define.operand_widths)
        if len(operands) != operand_count:
            return f"ERROR: operand len {len(operands)} does not match defined {operand_count}\n"
        if operand_count == 0:
            return define.name
        elif operand_count == 1:
            return f"{define.name} {operands[0]}"
        return f"ERROR: unhandled operand_count for {define.name}\n"


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
        operands[i] = read_uint16(ins[offset:offset + width])
        offset += width
    return operands, offset


def read_uint16(ins: bytes) -> int:
    """Read 2 bytes as big-endian unsigned short (0-65535)"""
    return struct.unpack('>H', ins[:2])[0]
