# -*- coding: utf-8 -*-
from abc import abstractmethod
from dataclasses import dataclass

INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"
NULL_OBJ = "NULL"


class Object:
    value=None

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
        return str(self.value)

    @classmethod
    def copy(cls, obj: Object):
        return cls(obj.value)


@dataclass
class Null(Object):

    def type(self) -> str:
        return NULL_OBJ

    def inspect(self) -> str:
        return 'null'


if __name__ == '__main__':
    print('obj')
