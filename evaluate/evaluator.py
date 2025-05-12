# -*- coding: utf-8 -*-
from monkey_ast.ast import *
from object.object import *


def evaluate_statements(statements: list[Statement]):
    result = None
    for stmt in statements:
        result = evaluate(stmt)
    return result


def evaluate(node: Node):
    if isinstance(node, IntegerLiteral):
        return Integer(node.value)
    elif isinstance(node, Program):
        return evaluate_statements(node.statements)
    elif isinstance(node, ExpressionStatement):
        return evaluate(node.expression)
    return None
