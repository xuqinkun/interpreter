# -*- coding: utf-8 -*-
from abc import abstractmethod
from dataclasses import dataclass
from typing import Dict, Callable, List
from monkey_code import code
from monkey_ast import ast

NULL_OBJ = "NULL"
INTEGER_OBJ = "INTEGER"
BOOLEAN_OBJ = "BOOLEAN"
RETURN_VALUE_OBJ = "RETURN_VALUE"
ERROR_OBJ = "ERROR"
FUNCTION_OBJ = "FUNCTION"
STRING_OBJ = "STRING"
BUILTIN_OBJ = "BUILTIN"
ARRAY_OBJ = "ARRAY"
HASH_OBJ = "HASH"
QUOTE_OBJ = "QUOTE"
MACRO_OBJ = "MACRO"
COMPILED_FUNCTION_OBJ = "COMPILED_FUNCTION_OBJ"
CLOSURE_OBJ = "CLOSURE"


@dataclass
class HashKey:
    key_type: str = None
    value: int = 0

    def __hash__(self):
        return hash(self.key_type) + hash(self.value)


def fnv1a_64(data):
    h = 0xcbf29ce484222325
    for b in data:
        h ^= b
        h *= 0x100000001b3
        h &= 0xFFFFFFFFFFFFFFFF
    return h


class Object:
    value = None

    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def inspect(self) -> str:
        pass


class Hashable(Object):

    @abstractmethod
    def hash_key(self) -> HashKey:
        pass

@dataclass
class Integer(Hashable):
    value: int

    def type(self) -> str:
        return INTEGER_OBJ

    def inspect(self) -> str:
        return str(self.value)

    def __repr__(self):
        return self.inspect()

    def hash_key(self) -> HashKey:
        return HashKey(self.type(), value=self.value)

    @classmethod
    def copy(cls, obj: Object):
        return cls(obj.value)


@dataclass
class Boolean(Hashable):
    value: bool

    def type(self) -> str:
        return BOOLEAN_OBJ

    def inspect(self) -> str:
        return str(self.value).lower()

    def hash_key(self):
        if self.value:
            value = 1
        else:
            value = 0
        return HashKey(self.type(), value)

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
    outer: 'Environment' = None

    def __init__(self):
        self.store = {}

    def get(self, name: str) -> Object:
        val = self.store.get(name, NULL)
        if val == NULL and self.outer:
            val = self.outer.get(name)
        return val

    def put(self, name: str, obj: Object) -> Object:
        self.store[name] = obj
        return obj

    @classmethod
    def new_enclosed_environment(cls, outer: 'Environment'):
        env = cls()
        env.outer = outer
        return env


@dataclass
class Function(Object):
    parameters: list[ast.Identifier] = None
    body: ast.BlockStatement = None
    env: Environment = None

    def type(self) -> str:
        return FUNCTION_OBJ

    def inspect(self) -> str:
        params = []
        for param in self.parameters:
            params.append(param.string())
        return f"fn({', '.join(params)}) {{\n{self.body.string()}\n}}"

    def __repr__(self):
        return self.inspect()

    @classmethod
    def copy(cls, func: Object):
        return cls(func.parameters, func.body, func.env)


@dataclass
class String(Hashable):
    value: str = None

    def type(self) -> str:
        return STRING_OBJ

    def inspect(self) -> str:
        return self.value

    def __repr__(self):
        return self.value

    @classmethod
    def copy(cls, obj: Object):
        return cls(obj.value)

    def hash_key(self) -> HashKey:
        hash_value = fnv1a_64(self.value.encode('utf-8'))
        return HashKey(self.type(), hash_value)


@dataclass
class Builtin(Object):
    fn: Callable = None

    def type(self) -> str:
        return BUILTIN_OBJ

    def inspect(self) -> str:
        return "builtin function"


@dataclass
class Array(Object):
    elements: list[Object] = None

    def type(self) -> str:
        return ARRAY_OBJ

    def inspect(self) -> str:
        elems = []
        for e in self.elements:
            elems.append(e.inspect())
        return f"[{', '.join(elems)}]"

    def __repr__(self):
        return self.inspect()


@dataclass
class HashPair:
    key: Object = None
    value: Object = None


@dataclass
class Hash(Object):
    pairs: Dict[HashKey, HashPair] = None

    def type(self) -> str:
        return HASH_OBJ

    def inspect(self) -> str:
        pairs = []
        for (_, pair) in self.pairs.items():
            pairs.append(f"{pair.key.inspect()}: {pair.value.inspect()}")
        return f"{{{', '.join(pairs)}}}"

    def __repr__(self):
        return self.inspect()


@dataclass
class Quote(Object):
    node: ast.Node = None

    def type(self) -> str:
        return QUOTE_OBJ

    def inspect(self) -> str:
        return f"QUOTE({self.node.string()})"


@dataclass
class Macro(Object):
    parameters: list[ast.Identifier] = None
    body: ast.BlockStatement = None
    env: Environment = None

    def type(self) -> str:
        return MACRO_OBJ

    def inspect(self) -> str:
        params = []
        if self.parameters:
            for p in self.parameters:
                params.append(p.string())
        body = ""
        if self.body:
            body = self.body.string()

        return f"macro ({', '.join(params)}) {{\n {body}\n}}"

    def __repr__(self):
        return self.inspect()


@dataclass
class CompiledFunction(Object):
    instructions: code.Instructions = None
    num_locals: int = 0
    num_parameters: int = 0

    def type(self) -> str:
        return COMPILED_FUNCTION_OBJ

    def inspect(self) -> str:
        return f"CompiledFunction {self}"


@dataclass
class Closure(Object):
    fn: CompiledFunction
    free: List[Object]

    def type(self) -> str:
        return CLOSURE_OBJ

    def inspect(self) -> str:
        return f"Closure {self}"