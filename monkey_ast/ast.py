from abc import abstractmethod
from dataclasses import dataclass
from monkey_token.token import Token

class Node:

    @abstractmethod
    def literal(self) -> str:
        pass

class Statement(Node):
    token=None
    expression=None


    @abstractmethod
    def statement(self):
        pass

    @abstractmethod
    def string(self):
        pass

class Expression(Node):
    token=None
    value=None
    operator=None
    left=None
    right=None

    @abstractmethod
    def expression(self):
        pass

    @abstractmethod
    def string(self):
        pass

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

@dataclass
class Identifier(Expression):
    token: Token
    value: str

    def literal(self):
        return self.token.literal

    def __repr__(self):
        return f"Identifier=(token={self.token}, value={self.value})"

    def string(self):
        return self.value

    def expression(self):
        pass


@dataclass
class LetStatement(Statement):
    token: Token
    name: Identifier=None
    value: Expression=None

    def literal(self):
        return self.token.literal

    def statement(self):
        pass

    def __repr__(self):
        return f"LetStatement(token='{self.token}', name='{self.name}', value={self.value})"

    def string(self):
        return f"{self.literal()} {self.name.string()} = {'' if self.value is None else self.value.string()};"


@dataclass
class ReturnStatement(Statement):
    token: Token=None
    return_value: Expression=None

    def literal(self):
        return self.token.literal

    def statement(self):
        pass

    def __repr__(self):
        return f"LetStatement(token='{self.token}', return_value='{self.return_value}')"

    def string(self):
        return f"{self.literal()} {'' if self.return_value is None else self.return_value};"


@dataclass
class ExpressionStatement(Statement):
    token: Token=None
    expression: Expression=None

    def literal(self):
        return self.token.literal

    def statement(self):
        return self.expression.literal()

    def __repr__(self):
        return f"ExpressionStatement(token='{self.token}', expression='{self.expression}')"

    def string(self):
        return "" if self.expression is None else self.expression.string()

    @classmethod
    def copy(cls, stmt: Statement):
        return cls(stmt.token, stmt.expression)

@dataclass
class IntegerLiteral(Expression):
    token: Token=None
    value: int=0

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        return self.token.literal

@dataclass
class PrefixExpression(Expression):
    token: Token=None
    operator: str=None
    right: Expression=None

    @classmethod
    def copy(cls, exp: Expression)->'PrefixExpression':
        return cls(exp.token, exp.operator, exp.right)

    def expression(self):
        pass

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        return f"({self.operator}{self.right.string()})"


@dataclass
class InfixExpression(Expression):
    token: Token=None
    operator: str=None
    left: Expression=None
    right: Expression=None

    @classmethod
    def copy(cls, exp: Expression)->'InfixExpression':
        return cls(exp.token, operator=exp.operator, left=exp.left, right=exp.right)

    def literal(self) -> str:
        return self.token.literal

    def string(self):
        return f"({self.left.string()} {self.operator} {self.right.string()})"

    def expression(self):
        pass