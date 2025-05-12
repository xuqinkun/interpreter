from typing import Dict

from evaluate import evaluator
from object.object import Object


class Environment:
    store: Dict[str, Object]=None

    def __init__(self):
        self.store = {}

    def get(self, name: str) -> Object:
        return self.store.get(name, evaluator.NULL)

    def put(self, name: str, obj: Object) -> Object:
        self.store[name] = obj
        return obj
