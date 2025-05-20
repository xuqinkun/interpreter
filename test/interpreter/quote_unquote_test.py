# -*- coding: utf-8 -*-

from util.test_util import *
from monkey_object.object import Quote


def test_quote_unquote():
    codes = [
        ('quote(5)', '5'),
        (
            "quote(5 + 8)",
            "(5 + 8)",
        ),
        (
            "quote(foobar)",
            "foobar",
        ),
        (
            "quote(foobar + barfoo)",
            "(foobar + barfoo)",
        ),
        (
            "quote(unquote(4))",
            "4",
        ),
        (
            "quote(unquote(4 + 4))",
            "8",
        ),
        (
            "quote(8 + unquote(4 + 4))",
            "(8 + 8)",
        ),
        (
            "quote(unquote(4 + 4) + 8)",
            "(8 + 8)",
        ),
        (
            "let foobar=8;quote(foobar)",
            "foobar",
        ),
        (
            "let foobar=8;quote(unquote(foobar))",
            "8",
        ),
        (
            "quote(unquote(true))",
            "true",
        ),
        (
            "quote(unquote(true == false))",
            "false",
        ),
        (
            """quote(unquote(quote(4 + 4)))""",
            """(4 + 4)""",
        ),
        (
            """let quotedInfixExpression = quote(4 + 4);
            quote(unquote(4 + 4) + unquote(quotedInfixExpression))""",
            """(8 + (4 + 4))""",
        ),
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
        test_quote_unquote
    ]
    run_cases(cases)
