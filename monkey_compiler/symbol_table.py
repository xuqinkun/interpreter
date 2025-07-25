from dataclasses import dataclass
from typing import Dict

GlobalScope = "GLOBAL"

@dataclass
class Symbol:
    name: str
    scope: str
    index: int

@dataclass
class SymbolTable:
    store: Dict[str, Symbol]
    num_definitions: int

    def __init__(self):
        self.store = {}
        self.num_definitions = 0

    def define(self, name):
        symbol = Symbol(name=name, index=self.num_definitions, scope=GlobalScope)
        self.store[name] = symbol
        self.num_definitions += 1
        return symbol

    def resolve(self, name):
        return self.store[name], name in self.store
