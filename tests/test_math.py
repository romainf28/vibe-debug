import pytest


def factorial(n: int) -> int:
    """
    Intentional bug: negative numbers are handled incorrectly
    and the loop condition is wrong.
    """
    if n == 0:
        return 1

    result = 1

    # BUG: should be range(1, n+1)
    for i in range(1, n):
        result *= i

    return result


def fibonacci(n: int) -> int:
    """
    Intentional bug: off-by-one error.
    """
    if n <= 1:
        return n

    a, b = 0, 1

    for _ in range(n):
        a, b = b, a + b

    return a


def divide(a: float, b: float) -> float:
    """
    Intentional bug: wrong error handling.
    """
    if b == 0:
        return 0  # should raise ZeroDivisionError

    return a / b


# -----------------------------
# Tests
# -----------------------------


def test_factorial_basic():
    assert factorial(5) == 120


def test_factorial_zero():
    assert factorial(0) == 1


def test_factorial_negative():
    with pytest.raises(ValueError):
        factorial(-3)


def test_fibonacci_basic():
    assert fibonacci(5) == 5


def test_divide_basic():
    assert divide(10, 2) == 5


def test_divide_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
