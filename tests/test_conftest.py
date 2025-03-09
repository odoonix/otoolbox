"""
    Dummy conftest.py for otoolbox.

    If you don't know what this is for, just leave it empty.
    Read more about conftest.py under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""
from otoolbox import environment

# import pytest
# tests/test_calculator.py

import pytest
# src/calculator.py


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b


def test_add():
    assert environment.context != None
    assert add(2, 3) == 5
    assert add(-1, 1) == 0


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 3) == -3


def test_multiply():
    assert multiply(2, 3) == 6
    assert multiply(-1, 3) == -3


def test_divide():
    """Test division"""
    assert divide(6, 3) == 2
    with pytest.raises(ValueError, match="Cannot divide by zero."):
        divide(1, 0)
