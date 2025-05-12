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


def eval_infix_expression(operator: str, left: object.Object, right: object.Object):
    if isinstance(left, object.Integer) and isinstance(right, object.Integer):
        return eval_integer_infix_expression(operator, left, right)
    if isinstance(left, object.Boolean) and isinstance(right, object.Boolean):
        return eval_boolean_infix_expression(operator, left, right)
    return NULL


def eval_integer_infix_expression(operator: str, left: object.Object, right: object.Object):
    left_val = left.value
    right_val = right.value
    if operator == '+':
        return object.Integer(left_val + right_val)
    elif operator == '-':
        return object.Integer(left_val - right_val)
    elif operator == '*':
        return object.Integer(left_val * right_val)
    elif operator == '/':
        return object.Integer(left_val / right_val)
    elif operator == '<':
        return native_bool_to_boolean_object(left_val < right_val)
    elif operator == '>':
        return native_bool_to_boolean_object(left_val > right_val)
    elif operator == '==':
        return native_bool_to_boolean_object(left_val == right_val)
    elif operator == '!=':
        return native_bool_to_boolean_object(left_val != right_val)
    return NULL


def eval_boolean_infix_expression(operator: str, left: object.Boolean, right: object.Boolean):
    if operator == '&&':
        return native_bool_to_boolean_object(left.value and right.value)
    elif operator == '||':
        return native_bool_to_boolean_object(left.value or right.value)
    elif operator == '==':
        return native_bool_to_boolean_object(left == right)
    elif operator == '!=':
        return native_bool_to_boolean_object(left != right)


def native_bool_to_boolean_object(obj: bool):
    if obj:
        return TRUE
    else:
        return FALSE


def evaluate(node: ast.Node):
    if isinstance(node, ast.IntegerLiteral):
        return object.Integer(node.value)
    if isinstance(node, ast.Boolean):
        return native_bool_to_boolean_object(node.value)
    elif isinstance(node, ast.Program):
        return evaluate_statements(node.statements)
    elif isinstance(node, ast.ExpressionStatement):
        return evaluate(node.expression)
    elif isinstance(node, ast.PrefixExpression):
        right = evaluate(node.right)
        return evaluate_prefix_expression(node.operator, right)
    elif isinstance(node, ast.InfixExpression):
        left = evaluate(node.left)
        right = evaluate(node.right)
        return eval_infix_expression(node.operator, left, right)
    return NULL
