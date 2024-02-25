"""Simple example for the calculator package."""
from calculator import Calculator


def example() -> None:
    """Present examples on how to use the calculator package."""
    calculator = Calculator()
    print("Example function for the calculator package.")  # noqa: T201
    print("Addition: 1 + 2 = ", calculator.add(1, 2))  # noqa: T201
    print("Subtraction: 1 - 2 = ", calculator.subtract(1, 2))  # noqa: T201
    print("Multiplication: 1 * 2 = ", calculator.multiply(1, 2))  # noqa: T201
    print("Division: 1 / 2 = ", calculator.divide(1, 2))  # noqa: T201


if __name__ == "__main__":
    example()
