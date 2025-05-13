# -*- coding: utf-8 -*-
from typing import List

from object.object import *


def evaluate_statements(statements: list[ast.Statement], env: Environment):
    result = NULL
    for stmt in statements:
        result = evaluate(stmt, env)
        if isinstance(result, ReturnValue):
            return result.value
        if isinstance(result, Error):
            return result
    return result


def evaluate_prefix_expression(op: str, right: Object):
    if op == '!':
        return eval_bang_expression(right)
    if op == '-':
        ret = eval_minus_expression(right)
        if ret == NULL:
            return Error(f"unknown operator: {op}{right.type()}")
        return Integer(-ret.value)
    return Error(f"unknown operator: {op}{right}")


def eval_bang_expression(right: Object):
    if right == TRUE:
        return FALSE
    elif right == FALSE:
        return TRUE
    elif right == NULL:
        return TRUE
    elif isinstance(right, Integer):
        if right.value == 0:
            return TRUE
        else:
            return FALSE
    return FALSE


def eval_minus_expression(right: Object):
    if isinstance(right, Integer):
        return Integer(right.value)
    return NULL


def eval_infix_expression(op: str, left: Object, right: Object):
    if isinstance(left, Integer) and isinstance(right, Integer):
        return eval_integer_infix_expression(op, left, right)
    if isinstance(left, Boolean) and isinstance(right, Boolean):
        return eval_boolean_infix_expression(op, left, right)
    return Error(f"type mismatch: {left.type()} {op} {right.type()}")


def eval_integer_infix_expression(op: str, left: Object, right: Object):
    left_val = left.value
    right_val = right.value
    if op == '+':
        return Integer(left_val + right_val)
    elif op == '-':
        return Integer(left_val - right_val)
    elif op == '*':
        return Integer(left_val * right_val)
    elif op == '/':
        return Integer(left_val / right_val)
    elif op == '&':
        return Integer(left_val & right_val)
    elif op == '|':
        return Integer(left_val | right_val)
    elif op == '<':
        return native_bool_to_boolean_object(left_val < right_val)
    elif op == '>':
        return native_bool_to_boolean_object(left_val > right_val)
    elif op == '==':
        return native_bool_to_boolean_object(left_val == right_val)
    elif op == '!=':
        return native_bool_to_boolean_object(left_val != right_val)
    return Error(f'unknown operator: {left.type()} {op} {right.type()}')


def eval_boolean_infix_expression(op: str, left: Boolean, right: Boolean):
    if op == '&&':
        return native_bool_to_boolean_object(left.value and right.value)
    elif op == '||':
        return native_bool_to_boolean_object(left.value or right.value)
    elif op == '==':
        return native_bool_to_boolean_object(left == right)
    elif op == '!=':
        return native_bool_to_boolean_object(left != right)

    return Error(f'unknown operator: {left.type()} {op} {right.type()}')


def native_bool_to_boolean_object(obj: bool):
    if obj:
        return TRUE
    else:
        return FALSE


def is_error(obj: Object):
    if obj is not None:
        return obj.type() == ERROR_OBJ
    return False


def evaluate(node: ast.Node, env: Environment):
    if isinstance(node, ast.IntegerLiteral):
        return Integer(node.value)
    if isinstance(node, ast.Boolean):
        return native_bool_to_boolean_object(node.value)
    elif isinstance(node, ast.Program):
        return evaluate_statements(node.statements, env)
    elif isinstance(node, ast.ExpressionStatement):
        return evaluate(node.expression, env)
    elif isinstance(node, ast.PrefixExpression):
        right = evaluate(node.right, env)
        if is_error(right):
            return right
        return evaluate_prefix_expression(node.operator, right)
    elif isinstance(node, ast.InfixExpression):
        left = evaluate(node.left, env)
        if is_error(left):
            return left
        right = evaluate(node.right, env)
        if is_error(right):
            return right
        return eval_infix_expression(node.operator, left, right)
    elif isinstance(node, ast.IFExpression):
        return eval_if_expression(node, env)
    elif isinstance(node, ast.BlockStatement):
        return evaluate_block_statement(node, env)
    elif isinstance(node, ast.ReturnStatement):
        val = evaluate(node.return_value, env)
        if is_error(val):
            return val
        return ReturnValue(val)
    elif isinstance(node, ast.LetStatement):
        val = evaluate(node.value, env)
        env.put(node.name.value, val)
        if is_error(val):
            return val
    elif isinstance(node, ast.Identifier):
        return eval_identifier(node, env)
    elif isinstance(node, ast.FunctionLiteral):
        params = node.parameters
        body = node.body
        return Function(parameters=params, body=body, env=env)
    elif isinstance(node, ast.CallExpression):
        func = evaluate(node.function, env)
        if is_error(func):
            return func
        arguments = eval_expressions(node.arguments, env)
        if len(arguments) == 1 and is_error(arguments[0]):
            return arguments[0]
        return apply_function(func, arguments)
    return NULL


def eval_expressions(args: List[ast.Expression], env: Environment) -> []:
    result = []
    for arg in args:
        ret = evaluate(arg, env)
        result.append(ret)
        if is_error(ret):
            return result
    return result


def apply_function(func: Function, args: List[Object]):
    env = Environment.new_enclosed_environment(func.env)
    for i, param in enumerate(func.parameters):
        env.put(param.value, args[i])
    ret = evaluate(func.body, env)
    if isinstance(ret, ReturnValue):
        return ret.value
    return ret


def eval_identifier(node: ast.Identifier, env: Environment):
    val = env.get(node.value)
    if val == NULL:
        return Error(f"identifier not found: {node.value}")
    return val


def eval_if_expression(node: ast.IFExpression, env: Environment):
    condition = evaluate(node.condition, env)
    if is_truthy(condition):
        return evaluate(node.consequence, env)
    else:
        return evaluate(node.alternative, env)


def is_truthy(obj: Object):
    if obj == NULL or obj == FALSE:
        return False
    else:
        return True


def evaluate_block_statement(block: ast.BlockStatement, env: Environment):
    statements = block.statements
    ret = NULL
    for stmt in statements:
        ret = evaluate(stmt, env)
        if isinstance(ret, Error):
            return ret
        if ret != NULL and isinstance(ret, ReturnValue):
            return ret
    return ret
