# -*- coding: utf-8 -*-

from util.test_util import *
from object.object import Quote


def test_quote():
    codes = [
        ('quote(5)', '5'),
    ]
    for code, expected in codes:
        ret = get_eval(code)
        if not isinstance(ret, Quote):
            cause = f"expected Quote, got {type(ret)} {ret}"
            return False, cause
        if ret.node is None:
            cause = "quote.node is None"
            return False, cause
        if ret.node.string() != expected:
            cause = f"not equal got:{ret.node.string()} expected:{expected}"
            return False, cause
    return True


if __name__ == '__main__':
    cases = [
        test_quote
    ]
    run_cases(cases)
