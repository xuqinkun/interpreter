from monkey_compiler.symbol_table import *


def test_define():
    expected = {
                "a": Symbol(name="a", scope=GlobalScope, index=0),
                "b": Symbol(name="b", scope=GlobalScope, index=1),
                "c": Symbol(name="c", scope=LocalScope, index=0),
                "d": Symbol(name="d", scope=LocalScope, index=1),
                "e": Symbol(name="e", scope=LocalScope, index=0),
                "f": Symbol(name="f", scope=LocalScope, index=1),
                }
    global_st = SymbolTable()
    a = global_st.define("a")
    if a != expected["a"]:
        print(f"expected a={expected["a"]} got={a}")
        return False
    b = global_st.define("b")
    if b != expected["b"]:
        print(f"expected b={expected["b"]} got={b}")
        return False
    first_local = SymbolTable.new_enclosed(global_st)
    c = first_local.define("c")
    if c != expected["c"]:
        print(f"expected c={expected["c"]} got={c}")
        return False
    d = first_local.define("d")
    if d != expected["d"]:
        print(f"expected d={expected["d"]} got={d}")
        return False
    second_local = SymbolTable.new_enclosed(first_local)
    e = second_local.define("e")
    if e != expected["e"]:
        print(f"expected e={expected["e"]} got={e}")
        return False
    f = second_local.define("f")
    if f != expected["f"]:
        print(f"expected f={expected["f"]} got={f}")
        return False
    return True


def test_resolve_global():
    global_st = SymbolTable()
    global_st.define("a")
    global_st.define("b")
    local = SymbolTable.new_enclosed(global_st)
    local.define("c")
    local.define("d")
    expected = (Symbol(name="a", scope=GlobalScope, index=0),
                Symbol(name="b", scope=GlobalScope, index=1),
                Symbol(name="c", scope=LocalScope, index=0),
                Symbol(name="d", scope=LocalScope, index=1),
                )
    for sym in expected:
        result, ok = local.resolve(sym.name)
        if not ok:
            print(f"name {sym.name} not resolvable")
            continue
        if result != sym:
            print(f"expected {sym.name} to resolve to {sym}, got={result}")
    return True


def test_resolve_nested_local():
    global_st = SymbolTable()
    global_st.define("a")
    global_st.define("b")

    first_local = SymbolTable.new_enclosed(global_st)
    first_local.define("c")
    first_local.define("d")

    second_local = SymbolTable.new_enclosed(first_local)
    second_local.define("e")
    second_local.define("f")
    expected = (
        (first_local,
                [Symbol(name="a", scope=GlobalScope, index=0),
                Symbol(name="b", scope=GlobalScope, index=1),
                Symbol(name="c", scope=LocalScope, index=0),
                Symbol(name="d", scope=LocalScope, index=1)]),
        (second_local,
         [Symbol(name="a", scope=GlobalScope, index=0),
          Symbol(name="b", scope=GlobalScope, index=1),
          Symbol(name="e", scope=LocalScope, index=0),
          Symbol(name="f", scope=LocalScope, index=1)]),
    )
    for case in expected:
        for sym in case[1]:
            result, ok = case[0].resolve(sym.name)
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
    if test_resolve_nested_local():
        print("test_resolve_global passed")