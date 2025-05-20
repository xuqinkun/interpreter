# -*- coding: utf-8 -*-
from monkey_ast.ast import *
from monkey_ast.modify import modify
from util.test_util import run_cases


def one():
    return IntegerLiteral(value=1)


def two():
    return IntegerLiteral(value=2)


def turn_one_to_two(node: Node):
    if not isinstance(node, IntegerLiteral):
        return node
    if node.value != 1:
        return node
    node.value = 2
    return node


def is_equal(modified: Node, expected: Node):
    if type(modified) != type(expected):
        return False, f"type is different, got: {type(modified)} want: {type(expected)}"
    node_type = type(modified)
    if node_type == Program:
        for stmt1, stmt2 in zip(modified.statements, expected.statements):
            if not is_equal(stmt1, stmt2):
                return False, f"not equal, got: {stmt1} want: {stmt2}"
    elif node_type == ExpressionStatement:
        output = is_equal(modified.expression, expected.expression)
        if type(output) == tuple:
            return output
        return True
    elif node_type == InfixExpression:
        output = is_equal(modified.left, expected.left)
        if type(output) == tuple:
            return output
        output = is_equal(modified.right, expected.right)
        if type(output) == tuple:
            return output
        if modified.operator != expected.operator:
            return False, f"operator not equal, got:{modified.operator} want: {expected.operator}"
    elif node_type == IFExpression:
        output = is_equal(modified.condition, expected.condition)
        if type(output) == tuple:
            return output
        output = is_equal(modified.consequence, expected.consequence)
        if type(output) == tuple:
            return output
        output = is_equal(modified.alternative, expected.alternative)
        if type(output) == tuple:
            return output
    elif node_type == BlockStatement:
        for stmt1, stmt2 in zip(modified.statements, expected.statements):
            output = is_equal(stmt1, stmt2)
            if type(output) == tuple:
                return False, f"not equal, got: {stmt1} want: {stmt2}"
    elif node_type == ReturnStatement:
        return is_equal(modified.return_value, expected.return_value)
    elif node_type == LetStatement:
        return is_equal(modified.value, expected.value)
    elif node_type == FunctionLiteral:
        output = is_equal(modified.parameters, expected.parameters)
        if type(output) == tuple:
            return output
        output = is_equal(modified.body, expected.body)
        if type(output) == tuple:
            return output
    elif node_type == list:
        for mod, exp in zip(modified, expected):
            output = is_equal(mod, exp)
            if type(output) == tuple:
                return output
    elif node_type == ArrayLiteral:
        output = is_equal(modified.elements, expected.elements)
        if type(output) == tuple:
            return output
    elif node_type == IntegerLiteral:
        if modified.value == expected.value:
            return True
        return False, f"not equal, got: {modified.value} want: {expected.value}"
    return False


def test_modify():
    tests = [
        (one(), two()),
        (
            Program(statements=[ExpressionStatement(expression=one())]),
            Program(statements=[ExpressionStatement(expression=two())])
        ),
        (
            InfixExpression(left=one(), operator="+", right=two()),
            InfixExpression(left=two(), operator="+", right=two()),
        ),
        (
            InfixExpression(left=two(), operator="+", right=one()),
            InfixExpression(left=two(), operator="+", right=two()),
        ),
        (
            PrefixExpression(operator="-", right=one()),
            PrefixExpression(operator="-", right=two()),
        ),
        (
            IndexExpression(left=one(), index=one()),
            IndexExpression(left=two(), index=two()),
        ),
        (
            IFExpression(
                condition=one(),
                consequence=BlockStatement(statements=[ExpressionStatement(expression=one())]),
                alternative=BlockStatement(statements=[ExpressionStatement(expression=two())]),
            ),
            IFExpression(
                condition=two(),
                consequence=BlockStatement(statements=[ExpressionStatement(expression=two())]),
                alternative=BlockStatement(statements=[ExpressionStatement(expression=two())]),
            )
        ),
        (
            ReturnStatement(return_value=one()),
            ReturnStatement(return_value=two())
        ),
        (
            LetStatement(value=one()),
            LetStatement(value=two())
        ),
        (
            FunctionLiteral(parameters=[],
                            body=BlockStatement(statements=
                                                [ExpressionStatement(expression=one())])),
            FunctionLiteral(parameters=[],
                            body=BlockStatement(statements=
                                                [ExpressionStatement(expression=two())]))
        ),
        (
            ArrayLiteral(elements=[one(), one()]),
            ArrayLiteral(elements=[two(), two()])
        ),
    ]
    for _input, expected in tests:
        modified = modify(_input, turn_one_to_two)
        output = is_equal(modified, expected)
        if type(output) == tuple:
            return False, f"not equal. got:{modified} expected:{expected}"
    hash_literal = HashLiteral(pairs={one(): one(), one(): one()})
    modify(hash_literal, turn_one_to_two)
    for k, v in hash_literal.pairs.items():
        if k.value != 2:
            return False, f"key is not 2, got {k.value}"
        if v.value != 2:
            return False, f"value is not 2, got {v.value}"
    return True


if __name__ == '__main__':
    run_cases([test_modify])
