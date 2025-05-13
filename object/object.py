# -*- coding: utf-8 -*-
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict

from monkey_ast import ast

NULL_OBJ = "NULL"
INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"
RETURN_VALUE_OBJ = "RETURN_VALUE"
ERROR_OBJ = "ERROR"
FUNCTON_OBJ = "FUNCTION"


class Object:
    value = None

    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def inspect(self) -> str:
        pass


@dataclass
class Integer(Object):
    value: int

    def type(self) -> str:
        return INTEGER_OBJ

    def inspect(self) -> str:
        return str(self.value)

    @classmethod
    def copy(cls, obj: Object):
        return cls(obj.value)


@dataclass
class Boolean(Object):
    value: bool

    def type(self) -> str:
        return BOOLEAN_OBJ

    def inspect(self) -> str:
        return str(self.value).lower()

    @classmethod
    def copy(cls, obj: Object):
        return cls(obj.value)


@dataclass
class Null(Object):

    def type(self) -> str:
        return NULL_OBJ

    def inspect(self) -> str:
        return 'null'


@dataclass
class ReturnValue(Object):
    value: Object

    def type(self) -> str:
        return RETURN_VALUE_OBJ

    def inspect(self) -> str:
        return self.value.inspect()


@dataclass
class Error(Object):
    message: str

    def type(self) -> str:
        return ERROR_OBJ

    def inspect(self) -> str:
        return "ERROR: " + self.message


NULL = Null()
TRUE = Boolean(True)
FALSE = Boolean(False)


class Environment:
    store: Dict[str, Object] = None

    def __init__(self):
        self.store = {}

    def get(self, name: str) -> Object:
        return self.store.get(name, NULL)

    def put(self, name: str, obj: Object) -> Object:
        self.store[name] = obj
        return obj


@dataclass
class Function(Object):
    parameters: list[ast.Identifier] = None
    body: ast.BlockStatement = None
    env: Environment = None

    def type(self) -> str:
        return FUNCTON_OBJ

    def inspect(self) -> str:
        params = []
        for param in self.parameters:
            params.append(param.string())
        return f"fn({', '.join(params)}) {{\n{self.body.string()}\n}}"

    @classmethod
    def copy(cls, func: Object):
        return cls(func.parameters, func.body, func.env)
