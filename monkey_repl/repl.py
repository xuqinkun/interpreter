# -*- coding: utf-8 -*-
import sys

from monkey_compiler import compiler
from monkey_parser.parser import parse
from monkey_vm import vm

PROMPT = ">>"

sys.setrecursionlimit(2000)


def match_eof(code: str):
    code = code.lower().strip()
    return code in ['q', 'quit', 'exit']


def run():
    while True:
        code = input(PROMPT)
        if match_eof(code):
            break
        if code:
            program = parse(code)

            comp = compiler.Compiler()
            err = comp.compile(program)
            if err is not None:
                print(f"Woops! Compilation failed: \n {err} \n")
                continue
            machine = vm.VM.new(comp.bytecode())
            err = machine.run()
            if err is not None:
                print(f"Woops! Execution bytecode failed: \n {err} \n")
                continue
            peek = machine.peek()
            print(peek.inspect())

    print('Bye bye!')


if __name__ == '__main__':
    run()
