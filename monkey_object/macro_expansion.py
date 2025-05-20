# -*- coding: utf-8 -*-
from monkey_ast import ast
from monkey_object import object
from util.test_util import check_type
from monkey_evaluate.evaluator import evaluate
from monkey_ast.modify import modify


def is_macro_definition(stmt: ast.Statement):
    let_stmt = check_type(ast.LetStatement, stmt)
    if type(let_stmt) == tuple:
        return False
    _, ok = check_type(ast.MacroLiteral, let_stmt.value)
    return ok


def add_macro(stmt: ast.Statement, env: object.Environment):
    let_stmt = check_type(ast.LetStatement, stmt)
    macro_literal, _ = check_type(ast.MacroLiteral, let_stmt.value)
    macro = object.Macro(parameters=macro_literal.parameters, env=env, body=macro_literal.body)
    env.put(let_stmt.name.value, macro)


def define_macro(program: ast.Program, env: object.Environment):
    definitions = []
    for i, stmt in enumerate(program.statements):
        if is_macro_definition(stmt):
            add_macro(stmt, env)
            definitions.append(i)
    for i in range(len(definitions) - 1, -1, -1):
        idx = definitions[i]
        program.statements.pop(idx)


def is_macro_call(exp: ast.CallExpression, env: object.Environment):
    identifier, ok = check_type(ast.Identifier, exp.function)
    if not ok:
        return None, False
    obj = env.get(identifier.value)
    if obj == object.NULL:
        return None, False
    if not isinstance(obj, object.Macro):
        return None, False
    return obj, True


def quote_args(exp: ast.CallExpression):
    args = []
    for arg in exp.arguments:
        args.append(object.Quote(arg))
    return args


def extend_macro_env(macro: object.Macro, args: list[object.Quote]):
    extended = object.Environment.new_enclosed_environment(macro.env)
    for i, param in enumerate(macro.parameters):
        extended.put(param.value, args[i])
    return extended


def expand_macro(program: ast.Program, env: object.Environment):
    def modifier(node: ast.Node):
        call, ok = check_type(ast.CallExpression, node)
        if not ok:
            return node
        macro, ok = is_macro_call(call, env)
        if not ok:
            return node
        args = quote_args(call)
        eval_env = extend_macro_env(macro, args)
        evaluated = evaluate(macro.body, eval_env)
        if not isinstance(evaluated, object.Quote):
            return f"we only supported returning AST-nodes from macros"
        return evaluated.node

    return modify(program, modifier)
