# -*- coding: utf-8 -*-
import sys
from typing import List, cast

from monkey_compiler import compiler
from monkey_compiler.symbol_table import SymbolTable
from monkey_object import object, builtins
from monkey_parser.parser import parse
from monkey_vm import vm
from monkey_vm.vm import GLOBAL_SIZE

PROMPT = ">>"

sys.setrecursionlimit(2000)


def match_eof(code: str):
    code = code.lower().strip()
    return code in ['q', 'quit', 'exit']


def run():
    constants = []
    global_variables = cast(List[object.Object], [None] * GLOBAL_SIZE)
    symbol_table = SymbolTable()
    for i, v in enumerate(builtins.builtins):
        symbol_table.define_builtin(i, v[0])
    while True:
        code = input(PROMPT)
        if match_eof(code):
            break
        if code:
            program = parse(code)
            comp = compiler.Compiler.new_with_state(symbol_table, constants)
            err = comp.compile(program)
            if err is not None:
                print(f"Woops! Compilation failed: \n {err} \n")
                continue
            code = comp.bytecode()
            constants = code.constants
            machine = vm.VM.new_with_global_state(code, global_variables)
            err = machine.run()
            if err is not None:
                print(f"Woops! Execution bytecode failed: \n {err} \n")
                continue
            peek = machine.last_popped_stack_elem()
            if peek is not None:
                print(peek.inspect())

    print('Bye bye!')


if __name__ == '__main__':
    run()
