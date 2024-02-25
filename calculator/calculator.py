"""Simple calculator class for basic arithmetic operations."""
from __future__ import annotations


class Calculator:

    """Calculator class for basic arithmetic operations."""

    def add(self, a: int | float, b: int | float) -> int | float:
        """Add two numbers together."""
        return a + b

    def subtract(self, a: int | float, b: int | float) -> int | float:
        """Subtract two numbers together.

        Subtracts b from a.
        """
        return a - b

    def multiply(self, a: int | float, b: int | float) -> int | float:
        """Multiply two numbers together."""
        return a * b

    def divide(self, a: int | float, b: int | float) -> int | float:
        """Divide two numbers together.

        Divides a by b.
        """
        return a / b
