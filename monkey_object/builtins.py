from monkey_object import object

def length(*args):
    arg = args[0]
    if len(args) != 1:
        return object.Error(f"wrong number of arguments. got={len(args)}, want=1")
    elif isinstance(arg, object.String):
        return object.Integer(len(arg.value))
    elif isinstance(arg, object.Array):
        return object.Integer(len(arg.elements))
    return object.Error(f"argument to 'len' not supported, got {arg.type()}")


def first(*args):
    arg = args[0]
    if len(args) != 1:
        return object.Error(f"wrong number of arguments. got {len(args)}, want 1")
    if arg.type() != object.ARRAY_OBJ:
        return object.Error(f"argument to 'first' must be ARRAY, got {arg.type()}")
    if len(arg.elements) > 0:
        return arg.elements[0]
    return object.NULL


def last(*args):
    arg = args[0]
    if len(args) != 1:
        return object.Error(f"wrong number of arguments. got {len(args)}, want 1")
    if arg.type() != object.ARRAY_OBJ:
        return object.Error(f"argument to 'last' must be ARRAY, got {arg.type()}")
    if len(arg.elements) > 0:
        return arg.elements[-1]
    return object.NULL


def rest(*args):
    arg = args[0]
    if len(args) != 1:
        return object.Error(f"wrong number of arguments. got {len(args)}, want 1")
    if arg.type() != object.ARRAY_OBJ:
        return object.Error(f"argument to 'last' must be object.Array, got {arg.type()}")
    if len(arg.elements) > 0:
        return object.Array(arg.elements[1:])
    return object.NULL


def push(*args):
    arg = args[0]
    obj = args[1]
    if len(args) != 2:
        return object.Error(f"wrong number of arguments. got {len(args)}, want 2")
    if arg.type() != object.ARRAY_OBJ:
        return object.Error(f"argument to 'push' must be ARRAY, got {arg.type()}")
    new_arr = arg.elements[:]
    new_arr.append(obj)
    return object.Array(new_arr)


def puts(*args):
    for arg in args:
        print(arg.inspect())
    return object.NULL

builtins = [
    ("len", object.Builtin(fn=length)),
    ("puts", object.Builtin(fn=puts)),
    ("first", object.Builtin(fn=first)),
    ("last", object.Builtin(fn=last)),
    ("rest", object.Builtin(fn=rest)),
    ("push", object.Builtin(fn=push)),
]