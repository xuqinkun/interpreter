# -*- coding: utf-8 -*-
import sys
from monkey_evaluate.evaluator import evaluate, NULL
from monkey_parser.parser import parse
from monkey_object.object import Environment
from monkey_object.macro_expansion import define_macro, expand_macro

PROMPT = ">>"

sys.setrecursionlimit(2000)


def match_eof(code: str):
    code = code.lower().strip()
    return code in ['q', 'quit', 'exit']


def run():
    env = Environment()
    macro_env = Environment()
    code = input(PROMPT)
    while not match_eof(code):
        if code:
            program = parse(code)
            define_macro(program, macro_env)
            expanded = expand_macro(program, macro_env)
            ret = evaluate(expanded, env)
            if ret != NULL:
                print(ret.inspect())
        code = input(PROMPT)
    print('Bye bye!')


if __name__ == '__main__':
    run()
