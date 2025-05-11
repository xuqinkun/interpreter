from abc import abstractmethod
from dataclasses import dataclass

from monkey_token.token import Token


class Node:

    @abstractmethod
    def literal(self) -> str:
        pass


class Statement(Node):
    token = None
    expression = None

    @abstractmethod
    def statement(self):
        pass

    @abstractmethod
    def string(self):
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
class Program:
    statements: list[Statement]

    def get_val(self):
        if len(self.statements) > 0:
            return self.statements[0].literal()
        else:
            return ""

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

    def expression(self):
        pass

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.value)


@dataclass
class LetStatement(Statement):
    token: Token
    name: Identifier = None
    value: Expression = None

    def literal(self):
        return self.token.literal

    def statement(self):
        pass

    def __repr__(self):
        return self.string()

    def string(self):
        return f"{self.literal()} {self.name.string()} = {'' if self.value is None else self.value.string()};"


@dataclass
class ReturnStatement(Statement):
    token: Token = None
    return_value: Expression = None

    def literal(self):
        return self.token.literal

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
        return self.string()


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

    def __repr__(self):
        return str(self.value)

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
        return "".join(lines)


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
        stem = f"if {condition} {consequence}"
        if self.alternative is None:
            return stem
        else:
            return f"{stem} else {self.alternative.string()}"

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
        for p in self.parameters:
            params.append(p.string())
        param = ','.join(params)
        return f"{self.token.literal}({param}) {self.body.string()}"

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

    @classmethod
    def copy(cls, exp: Expression):
        return cls(exp.token, exp.function, exp.arguments)