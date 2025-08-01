from dataclasses import dataclass
from typing import Dict, Optional, List

GlobalScope = "GLOBAL"
LocalScope = "LOCAL"
BuiltinScope = "BUILTIN"
FreeScope = "FREE"

@dataclass
class Symbol:
    name: str=None
    scope: str=None
    index: int=0

@dataclass
class SymbolTable:
    store: Dict[str, Symbol]
    num_definitions: int
    outer: Optional["SymbolTable"]
    free_symbols: List[Symbol] = None

    def __init__(self):
        self.store = {}
        self.num_definitions = 0
        self.outer = None
        self.free_symbols = []

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
            obj, ok = self.outer.resolve(name)
            if not ok:
                return obj, ok
            if obj.scope == GlobalScope or obj.scope == BuiltinScope:
                return obj, ok
            # 来自函数的外层作用域，既不是局部的也不是全局的
            free = self.define_free(obj)
            return free, True
        return obj, name in self.store

    def define_builtin(self, index: int, name: str):
        symbol = Symbol(name=name, index=index, scope=BuiltinScope)
        self.store[name] = symbol
        return symbol

    def define_free(self, original: Symbol):
        self.free_symbols.append(original)
        symbol = Symbol(name=original.name, index=len(self.free_symbols) - 1)
        symbol.scope = FreeScope
        self.store[original.name] = symbol
        return symbol

    @staticmethod
    def new_enclosed(outer: Optional["SymbolTable"]):
        s = SymbolTable()
        s.outer = outer
        return s
