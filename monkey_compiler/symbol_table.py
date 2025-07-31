from dataclasses import dataclass
from typing import Dict, Optional

GlobalScope = "GLOBAL"
LocalScope = "LOCAL"
BuiltinScope = "BUILTIN"

@dataclass
class Symbol:
    name: str
    scope: str
    index: int

@dataclass
class SymbolTable:
    store: Dict[str, Symbol]
    num_definitions: int
    outer: Optional["SymbolTable"]

    def __init__(self):
        self.store = {}
        self.num_definitions = 0
        self.outer = None

    def define(self, name):
        symbol = Symbol(name=name, index=self.num_definitions, scope=GlobalScope)
        if self.outer is None:
            symbol.scope = GlobalScope
        else:
            symbol.scope = LocalScope
        self.store[name] = symbol
        self.num_definitions += 1
        return symbol

    def resolve(self, name):
        obj = self.store.get(name, None)
        if obj is None and self.outer is not None:
            return self.outer.resolve(name)
        return obj, name in self.store

    def define_builtin(self, index: int, name: str):
        symbol = Symbol(name=name, index=index, scope=BuiltinScope)
        self.store[name] = symbol
        return symbol

    @staticmethod
    def new_enclosed(outer: Optional["SymbolTable"]):
        s = SymbolTable()
        s.outer = outer
        return s
