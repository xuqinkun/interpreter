from monkey_compiler.symbol_table import *


def test_define():
    expected = {"a": Symbol(name="a", scope=GlobalScope, index=0),
                "b": Symbol(name="b", scope=GlobalScope, index=1)
                }
    st = SymbolTable()
    a = st.define("a")
    if a != expected["a"]:
        print(f"expected a={expected["a"]} got={a}")
        return False
    b = st.define("b")
    if b != expected["b"]:
        print(f"expected b={expected["b"]} got={b}")
        return False
    return True


def test_resolve_global():
    st = SymbolTable()
    st.define("a")
    st.define("b")
    expected = (Symbol(name="a", scope=GlobalScope, index=0),
                Symbol(name="b", scope=GlobalScope, index=1)
                )
    for sym in expected:
        result, ok = st.resolve(sym.name)
        if not ok:
            print(f"name {sym.name} not resolvable")
            continue
        if result != sym:
            print(f"expected {sym.name} to resolve to {sym}, got={result}")
    return True


if __name__ == '__main__':
    if test_define():
        print("test define passed")
    if test_resolve_global():
        print("test_resolve_global passed")