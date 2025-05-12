# -*- coding: utf-8 -*-
from monkey_ast import ast
from object import object

NULL = object.Null()
TRUE = object.Boolean(True)
FALSE = object.Boolean(False)


def evaluate_statements(statements: list[ast.Statement]):
    result = NULL
    for stmt in statements:
        result = evaluate(stmt)
    return result


def evaluate_prefix_expression(op: str, right: object.Object):
    if op == '!':
        return eval_bang_expression(right)
    if op == '-':
        right = eval_minus_expression(right)
        return object.Integer(-right.value)
    return NULL


def eval_bang_expression(right: object.Object):
    if right == TRUE:
        return FALSE
    elif right == FALSE:
        return TRUE
    elif right == NULL:
        return TRUE
    elif isinstance(right, object.Integer):
        if right.value == 0:
            return TRUE
        else:
            return FALSE
    return FALSE


def eval_minus_expression(right: object.Object):
    if isinstance(right, object.Integer):
        return object.Integer(right.value)
    return NULL


def evaluate(node: ast.Node):
    if isinstance(node, ast.IntegerLiteral):
        return object.Integer(node.value)
    if isinstance(node, ast.Boolean):
        if node.value:
            return TRUE
        else:
            return FALSE
    elif isinstance(node, ast.Program):
        return evaluate_statements(node.statements)
    elif isinstance(node, ast.ExpressionStatement):
        return evaluate(node.expression)
    elif isinstance(node, ast.PrefixExpression):
        right = evaluate(node.right)
        return evaluate_prefix_expression(node.operator, right)
    return NULL
