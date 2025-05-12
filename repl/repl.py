# -*- coding: utf-8 -*-
from evaluate.evaluator import evaluate, NULL
from monkey_parser.parser import parse

PROMPT = ">>"


def match_eof(code: str):
    code = code.lower().strip()
    return code in ['q', 'quit', 'exit']


def run():
    code = input(PROMPT)
    while not match_eof(code):
        if code:
            program = parse(code)
            ret = evaluate(program)
            if ret != NULL:
                print(ret.inspect())
        code = input(PROMPT)
    print('Bye bye!')


if __name__ == '__main__':
    run()
