# -*- coding: utf-8 -*-
from evaluate.evaluator import evaluate
from monkey_parser.parser import parse

PROMPT = ">>"


def match_eof(code: str):
    code = code.lower().strip()
    return code in ['q', 'quit', 'exit']


def start():
    code = input(PROMPT)
    while not match_eof(code):
        program = parse(code)
        ret = evaluate(program)
        print(ret.inspect())
        code = input(PROMPT)


if __name__ == '__main__':
    start()
