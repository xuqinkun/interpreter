from abc import abstractmethod
from dataclasses import dataclass
from monkey_token.token import Token

class Node:

    @abstractmethod
    def literal(self) -> str:
        pass

class Statement(Node):

    @abstractmethod
    def statement(self):
        pass

class Expression(Node):

    @abstractmethod
    def expression(self):
        pass

@dataclass
class Program:
    statements: list[Statement]

    def get_val(self):
        if len(self.statements) > 0:
            return self.statements[0].literal()
        else:
            return ""

@dataclass
class Identifier:
    token: Token
    value: str

    def literal(self):
        return self.token.literal

    def __repr__(self):
        return f"Identifier=(token={self.token}, value={self.value})"


@dataclass
class LetStatement(Statement):
    token: Token
    name: Identifier=None
    value: Expression=None

    def literal(self):
        return self.token.literal

    def __repr__(self):
        return f"LetStatement(token='{self.token}', name='{self.name}', value={self.value})"

@dataclass()
class ReturnStatement(Statement):
    token: Token=None
    return_value: Expression=None

    def literal(self):
        return self.token.literal