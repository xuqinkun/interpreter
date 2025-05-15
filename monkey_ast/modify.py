# -*- coding: utf-8 -*-
from typing import Callable

from monkey_ast.ast import *


def modify(node: Node, modifier: Callable[[Node], Node]) -> Node:
    if isinstance(node, Program):
        for i, stmt in enumerate(node.statements):
            node.statements[i] = modify(stmt, modifier)
    elif isinstance(node, ExpressionStatement):
        node.expression = modify(node.expression, modifier)
    elif isinstance(node, InfixExpression):
        node.left = modify(node.left, modifier)
        node.right = modify(node.right, modifier)
    elif isinstance(node, PrefixExpression):
        node.right = modify(node.right, modifier)
    elif isinstance(node, IndexExpression):
        node.left = modify(node.left, modifier)
        node.index = modify(node.index, modifier)
    elif isinstance(node, IFExpression):
        node.condition = modify(node.condition, modifier)
        node.consequence = modify(node.consequence, modifier)
        node.alternative = modify(node.alternative, modifier)
    elif isinstance(node, BlockStatement):
        for i, stmt in enumerate(node.statements):
            node.statements[i] = modify(stmt, modifier)
    elif isinstance(node, ReturnStatement):
        node.return_value = modify(node.return_value, modifier)
    elif isinstance(node, LetStatement):
        node.value = modify(node.value, modifier)
    elif isinstance(node, FunctionLiteral):
        for i, param in enumerate(node.parameters):
            node.parameters[i] = modify(param, modifier)
        node.body = modify(node.body, modifier)
    elif isinstance(node, ArrayLiteral):
        for i, e in enumerate(node.elements):
            node.elements[i] = modify(e, modifier)
    elif isinstance(node, HashLiteral):
        new_pairs = {}
        for k, v in node.pairs.items():
            new_key = modify(k, modifier)
            new_val = modify(v, modifier)
            new_pairs[new_key] = new_val
        node.pairs = new_pairs
    return modifier(node)

