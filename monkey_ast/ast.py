from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict

from monkey_token.token import Token


class Node:

    @abstractmethod
    def literal(self) -> str:
        pass

    @abstractmethod
    def string(self) -> str:
        pass


class Statement(Node):
    token = None
    expression = None

    @abstractmethod
    def statement(self):
        pass

    @abstractmethod
    def string(self) -> str:
        pass

    def __repr__(self):
        return self.string()


class Expression(Node):
    token = None
    value = None
    operator = None
    left = None
    right = None

    @abstractmethod
    def expression(self):
        pass

    @abstractmethod
    def string(self):
        pass

    def __repr__(self):
        return self.string()


@dataclass
class Program(Node):
    statements: list[Statement]

    def get_val(self):
        if len(self.statements) > 0:
            return self.statements[0].literal()
        else:
            return ""

    def literal(self) -> str:
        return "program"

    def string(self):
        s = []
        for stmt in self.statements:
            s.append(stmt.string())
        return "".join(s)

    def __repr__(self):
        return self.string()


@dataclass
class Identifier(Expression):
    token: Token
    value: str

    def literal(self):
        return self.token.literal

    def __repr__(self):
        return self.string()

    def string(self):
        return self.value

    def __hash__(self):
        return hash(self.value)

    def expression(self):
        pass

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.value)


@dataclass
class LetStatement(Statement):
    token: Token = None
    name: Identifier = None
    value: Expression = None

    def literal(self):
        if self.token:
            return self.token.literal
        else:
            return ""

    def statement(self):
        pass

    def __repr__(self):
        return self.string()

    def string(self):
        exp = '' if self.value is None else self.value.string()
        name = '' if self.name is None else self.name.string()
        return f"{self.literal()} {name} = {self.value};"

    @classmethod
    def copy(cls, stmt: Statement):
        return cls(stmt.token, stmt.name, stmt.value)


@dataclass
class ReturnStatement(Statement):
    token: Token = None
    return_value: Expression = None

    def literal(self):
        return self.token.literal if self.token is not None else ''

    def statement(self):
        pass

    def __repr__(self):
        return self.string()

    def string(self):
        return f"{self.literal()} {'' if self.return_value is None else self.return_value};"


@dataclass
class ExpressionStatement(Statement):
    token: Token = None
    expression: Expression = None

    def literal(self):
        return self.token.literal

    def statement(self):
        return self.expression.literal()

    def string(self):
        return "" if self.expression is None else self.expression.string()

    @classmethod
    def copy(cls, stmt: Statement):
        return cls(stmt.token, stmt.expression)

    def __repr__(self):
        if self.expression is None:
            return self.token.literal
        return f"{self.string()}"


@dataclass
class IntegerLiteral(Expression):
    token: Token = None
    value: int = 0

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        return str(self.value)

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return str(self.value)

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.value)


@dataclass
class StringLiteral(Expression):
    token: Token = None
    value: str = None

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        return f'{self.value}'

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return self.string()

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.value)


@dataclass
class PrefixExpression(Expression):
    token: Token = None
    operator: str = None
    right: Expression = None

    @classmethod
    def copy(cls, exp: Expression) -> 'PrefixExpression':
        return cls(exp.token, exp.operator, exp.right)

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        right = "" if self.right is None else self.right.string()
        return f"({self.operator}{right})"

    def __repr__(self):
        return self.string()


@dataclass
class InfixExpression(Expression):
    token: Token = None
    operator: str = None
    left: Expression = None
    right: Expression = None

    @classmethod
    def copy(cls, exp: Expression) -> 'InfixExpression':
        return cls(exp.token, operator=exp.operator, left=exp.left, right=exp.right)

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        left = "" if self.left is None else self.left.string()
        right = "" if self.right is None else self.right.string()
        return f"({left} {self.operator} {right})"

    def expression(self):
        pass

    def __hash__(self):
        return hash(self.operator) + hash(self.left) + hash(self.right)

    def __repr__(self):
        return self.string()


@dataclass
class Boolean(Expression):
    token: Token
    value: bool

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        return self.token.literal

    def __hash__(self):
        return hash(self.value)

    def __repr__(self):
        return self.string()

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.value)


@dataclass
class BlockStatement(Statement):
    token: Token = None
    statements: list[Statement] = None

    def statement(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        lines = []
        for stmt in self.statements:
            lines.append(stmt.string())
        return ";".join(lines)

    def __repr__(self):
        return self.string()


@dataclass
class IFExpression(Expression):
    token: Token = None
    condition: Expression = None
    consequence: BlockStatement = None
    alternative: BlockStatement = None

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        condition = self.condition.string()
        consequence = self.consequence.string()
        stem = f"if ({condition}) {{{consequence}}}"
        if self.alternative is None:
            return stem
        else:
            return f"{stem} else {{{self.alternative.string()}}}"

    def __repr__(self):
        return self.string()

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.condition, exp.consequence, exp.alternative)


@dataclass
class FunctionLiteral(Expression):
    token: Token = None
    parameters: list[Identifier] = None
    body: BlockStatement = None

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        params = []
        if self.parameters:
            for p in self.parameters:
                params.append(p.string())
        param = ','.join(params)
        return f"{self.token.literal}({param}) {{{self.body.string()}}}"

    def __repr__(self):
        return self.string()

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.parameters, exp.body)


@dataclass
class CallExpression(Expression):
    token: Token = None
    function: Expression = None
    arguments: list[Expression] = None

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        args = []
        for arg in self.arguments:
            args.append(arg.string())
        return f"{self.function.string()}({', '.join(args)})"

    def __repr__(self):
        return self.string()

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.function, exp.arguments)


@dataclass
class ArrayLiteral(Expression):
    token: Token = None
    elements: list[Expression] = None

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        elems = []
        for elem in self.elements:
            elems.append(elem.string())
        return f"[{', '.join(elems)}]"

    def __repr__(self):
        return self.string()

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.elements)


@dataclass
class HashLiteral(Expression):
    token: Token = None
    pairs: Dict[Expression, Expression] = None

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        pairs = {}
        for key, val in self.pairs.items():
            if isinstance(key, str):
                pairs[key] = val.string()
            else:
                pairs[key.string()] = val.string()
        joined_items = ",".join(f"{k}:{v}" for k, v in pairs.items())
        return f"{{{joined_items}}}"

    def __repr__(self):
        return self.string()

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.pairs)


@dataclass
class IndexExpression(Expression):
    token: Token = None
    left: Expression = None
    index: Expression = None

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        return f"({self.left.string()}[{self.index.string()}])"

    def __repr__(self):
        return self.string()

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.left, exp.index)


@dataclass
class MacroLiteral(Expression):
    token: Token = None
    parameters: list[Expression] = None
    body: BlockStatement = None

    def expression(self):
        pass

    def literal(self) -> str:
        if self.token:
            return self.token.literal
        else:
            return ""

    def string(self):
        params = []
        if self.parameters:
            for param in self.parameters:
                params.append(param.string())
        body = ""
        if self.body:
            body = self.body.string()
        return f"{self.literal()}({', '.join(params)}) {{{body}}}"

    def __repr__(self):
        return self.string()

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.parameters, exp.body)
