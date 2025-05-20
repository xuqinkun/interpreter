# -*- coding: utf-8 -*-
from monkey_ast import ast
from monkey_object import object
from monkey_ast import modify
from monkey_token import token


def check_type(expected_type: type, obj: object.Object):
    if isinstance(obj, object.Error):
        return obj
    if not isinstance(obj, expected_type):
        return False, f"Wrong type error, expected: {expected_type} actual:{type(obj)}"
    return expected_type.copy(obj)


def quote(node: ast.Node, env: object.Environment):
    node = eval_unquote_calls(node, env)
    return object.Quote(node)


def convert_object_to_ast_node(obj: object.Object):
    if isinstance(obj, object.Integer):
        t = token.Token(token.INT, obj.inspect())
        return ast.IntegerLiteral(t, obj.value)
    elif isinstance(obj, object.Boolean):
        if obj.value:
            tok = token.Token(token.TRUE, 'true')
        else:
            tok = token.Token(token.FALSE, 'false')
        return ast.Boolean(tok, obj.value)
    elif isinstance(obj, object.Quote):
        return obj.node
    return None


def eval_unquote_calls(node: ast.Expression, env: object.Environment):
    from monkey_evaluate.evaluator import evaluate
    def modifier(node):
        output = is_unquote_call(node)
        if type(output) == tuple:
            return node
        call = ast.CallExpression.copy(node)
        if len(call.arguments) != 1:
            return node
        unquoted = evaluate(call.arguments[0], env)
        return convert_object_to_ast_node(unquoted)

    return modify.modify(node, modifier=modifier)


def is_unquote_call(node: ast.Node):
    caller = check_type(ast.CallExpression, node)
    if type(caller) == tuple:
        return caller
    return caller.function.literal == 'unquote'
