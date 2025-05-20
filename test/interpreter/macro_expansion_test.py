# -*- coding: utf-8 -*-
from monkey_object import object
from util.test_util import *
from monkey_object.macro_expansion import define_macro, expand_macro


def test_define_macro():
    code = """
        let number = 1;
        let function = fn(x, y) {x+y};
        let mymacro = macro(x,y) {x+y;};
    """
    env = object.Environment()
    program = parse(code)
    define_macro(program, env)
    if len(program.statements) != 2:
        return False, f"Wrong number of statements. got {len(program.statements)}"
    number = env.get("number")
    if number != object.NULL:
        return False, "number should not be defined"
    function = env.get("function")
    if function != object.NULL:
        return False, "function should not be defined"
    obj = env.get("mymacro")
    if obj == object.NULL:
        return False, "macro not in env"
    if not isinstance(obj, object.Macro):
        return False, f"object is not Macro, get {type(obj)}"
    if len(obj.parameters) != 2:
        return False, f"Wrong number of macro parameters, got {len(obj.parameters)}"
    if obj.parameters[0].string() != 'x':
        return False, f"parameter is not 'x' got {obj.parameters[0]}"
    if obj.parameters[1].string() != 'y':
        return False, f"parameter is not 'y' got {obj.parameters[1]}"
    expected_body = "(x + y)"
    if obj.body.string() != expected_body:
        return False, f"body is not {expected_body} got {obj.body.string()}"
    return True


def test_expand_macro():
    cases = [(
        """
        let infixExpression = macro() { quote(1 + 2); };

        infixExpression();
        """,
        """(1 + 2)""",
    ),
        (
            """
            let reverse = macro(a, b) { quote(unquote(b) - unquote(a)); };
    
            reverse(2 + 2, 10 - 5);
            """,
            """(10 - 5) - (2 + 2)""",
        ),
        (
            """
            let unless = macro(condition, consequence, alternative) {
                quote(if (!(unquote(condition))) {
                    unquote(consequence);
                } else {
                    unquote(alternative);
                });
            };

            unless(10 > 5, puts("not greater"), puts("greater"));
            """,
            """if (!(10 > 5)) { puts("not greater") } else { puts("greater") }""",
        ),
    ]
    for code, expected_code in cases:
        program = parse(code)
        expected = parse(expected_code)
        env = object.Environment()
        define_macro(program, env)
        expanded = expand_macro(program, env)
        if type(expanded) == tuple:
            return expanded
        if expanded.string() != expected.string():
            return False, f"not equal, want {expected.string()} got {expanded.string()}"
    return True


if __name__ == '__main__':
    tests = [
        test_define_macro,
        test_expand_macro
    ]
    run_cases(tests)
