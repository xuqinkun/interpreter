# -*- coding: utf-8 -*-
from typing import List
from object.object import *


def length(*args):
    arg = args[0]
    if len(args) != 1:
        return Error(f"wrong number of arguments. got {len(args)}, want 1")
    elif isinstance(arg, String):
        return Integer(len(arg.value))
    elif isinstance(arg, Array):
        return Integer(len(arg.elements))
    return Error(f"argument to 'len' not supported, got {arg.type()}")


def first(*args):
    arg = args[0]
    if len(args) != 1:
        return Error(f"wrong number of arguments. got {len(args)}, want 1")
    if arg.type() != ARRAY_OBJ:
        return Error(f"argument to 'first' must be ARRAY, go {arg.type()}")
    if len(arg.elements) > 0:
        return arg.elements[0]
    return NULL


def last(*args):
    arg = args[0]
    if len(args) != 1:
        return Error(f"wrong number of arguments. got {len(args)}, want 1")
    if arg.type() != ARRAY_OBJ:
        return Error(f"argument to 'last' must be ARRAY, go {arg.type()}")
    if len(arg.elements) > 0:
        return arg.elements[-1]
    return NULL


def rest(*args):
    arg = args[0]
    if len(args) != 1:
        return Error(f"wrong number of arguments. got {len(args)}, want 1")
    if arg.type() != ARRAY_OBJ:
        return Error(f"argument to 'last' must be ARRAY, go {arg.type()}")
    if len(arg.elements) > 0:
        return Array(arg.elements[1:])
    return NULL


def push(*args):
    arg = args[0]
    obj = args[1]
    if len(args) != 2:
        return Error(f"wrong number of arguments. got {len(args)}, want 2")
    if arg.type() != ARRAY_OBJ:
        return Error(f"argument to 'last' must be ARRAY, go {arg.type()}")
    new_arr = arg.elements[:]
    new_arr.append(obj)
    return Array(new_arr)


def push(*args):
    for arg in args:
        print(arg.inspect())
    return NULL


builtin_obj = {
    "len": Builtin(fn=length),
    "first": Builtin(fn=first),
    "last": Builtin(fn=last),
    "rest": Builtin(fn=rest),
    "push": Builtin(fn=push),
    "puts": Builtin(fn=push),
}


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
    elif isinstance(left, Boolean) and isinstance(right, Boolean):
        return eval_boolean_infix_expression(op, left, right)
    elif isinstance(left, String) and isinstance(right, String):
        return eval_string_infix_expression(op, left, right)
    return Error(f"type mismatch: {left.type()} {op} {right.type()}")


def eval_string_infix_expression(op: str, left: Object, right: Object):
    if op != '+':
        return Error(f'unknown operator: {left.type()} {op} {right.type()}')
    return String(left.value + right.value)


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
    elif isinstance(node, ast.StringLiteral):
        return String(node.value)
    elif isinstance(node, ast.ArrayLiteral):
        elements = eval_expressions(node.elements, env)
        if len(elements) == 1 and is_error(elements[0]):
            return elements[0]
        return Array(elements=elements)
    elif isinstance(node, ast.IndexExpression):
        left = evaluate(node.left, env)
        if is_error(left):
            return left
        index = evaluate(node.index, env)
        if is_error(index):
            return index
        return eval_index_expression(left, index)
    elif isinstance(node, ast.HashLiteral):
        return eval_hash_literal(node, env)
    return NULL


def eval_hash_literal(node: ast.HashLiteral, env: Environment):
    pairs = {}
    for key_node, val_node in node.pairs.items():
        key = evaluate(key_node, env)
        if is_error(key):
            return key
        value = evaluate(val_node, env)
        hashed = key.hash_key()
        pairs[hashed] = HashPair(key, value)
    return Hash(pairs)


def eval_index_expression(left: Object, index: Object):
    if left.type() == ARRAY_OBJ and index.type() == INTEGER_OBJ:
        return eval_array_index_expression(left, index)
    elif left.type() == HASH_OBJ:
        return eval_hash_index_expression(left, index)
    else:
        return Error(f"index operator not supported: {left.type()}")


def eval_hash_index_expression(left: Hash, index: String):
    pair = left.pairs.get(index.hash_key(), NULL)
    if pair is NULL:
        return pair
    return pair.value


def eval_array_index_expression(left: Array, index: Object):
    idx = index.value
    max_len = len(left.elements)
    if idx < 0 or idx >= max_len:
        return NULL
    return left.elements[idx]


def eval_expressions(args: List[ast.Expression], env: Environment) -> []:
    result = []
    if args is None:
        return result
    for arg in args:
        ret = evaluate(arg, env)
        result.append(ret)
        if is_error(ret):
            return result
    return result


def apply_function(func: Function, args: List[Object]):
    if isinstance(func, Builtin):
        return func.fn(*args)
    if isinstance(func, Function):
        env = Environment.new_enclosed_environment(func.env)
        for i, param in enumerate(func.parameters):
            env.put(param.value, args[i])
        ret = evaluate(func.body, env)
        if isinstance(ret, ReturnValue):
            return ret.value
        return ret
    return Error(f"not a function: {func.type()}")


def eval_identifier(node: ast.Identifier, env: Environment):
    val = env.get(node.value)
    if val != NULL:
        return val
    builtin = builtin_obj.get(node.value)
    if builtin:
        return builtin
    return Error(f"identifier not found: {node.value}")


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
