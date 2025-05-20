from parser_test import run_cases
from monkey_object.object import String


def test_string_hash_key():
    hello1 = String("Hello World")
    hello2 = String("Hello World")
    diff1 = String("My name is johnny")
    diff2 = String("My name is johnny")

    if hello1.hash_key() != hello2.hash_key():
        return False, "strings with same content have different hash keys"

    if diff1.hash_key() != diff2.hash_key():
        return False, "strings with same content have different hash keys"

    if hello1.hash_key() == diff1.hash_key():
        return False, "strings with different content have same hash keys"
    return True


if __name__ == '__main__':
    cases = [
        test_string_hash_key
    ]
    run_cases(cases)
