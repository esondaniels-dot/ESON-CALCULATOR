"""Safe arithmetic expression parser for ESON CALCULATOR."""
from __future__ import annotations

import math
import re


class CalculationError(ValueError):
    """Invalid or undefined calculator expression."""


_TOKEN = re.compile(r"(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?|[+\-*/^()%√]" )


def _tokenize(expression: str) -> list[str]:
    expression = expression.replace("×", "*").replace("÷", "/").replace("−", "-").replace(" ", "")
    if not expression:
        raise CalculationError("Enter a calculation")
    tokens: list[str] = []
    pos = 0
    while pos < len(expression):
        match = _TOKEN.match(expression, pos)
        if not match:
            raise CalculationError("Invalid expression")
        tokens.append(match.group(0))
        pos = match.end()
    return tokens


class _Parser:
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.index = 0

    def peek(self) -> str | None:
        return self.tokens[self.index] if self.index < len(self.tokens) else None

    def take(self) -> str:
        token = self.peek()
        if token is None:
            raise CalculationError("Incomplete expression")
        self.index += 1
        return token

    def parse(self) -> float:
        value = self.expression()
        if self.peek() is not None:
            raise CalculationError("Invalid expression")
        if not math.isfinite(value):
            raise CalculationError("Result is out of range")
        return value

    def expression(self) -> float:
        value = self.term()
        while self.peek() in ("+", "-"):
            op = self.take()
            rhs = self.term()
            value = value + rhs if op == "+" else value - rhs
        return value

    def term(self) -> float:
        value = self.unary()
        while self.peek() in ("*", "/"):
            op = self.take()
            rhs = self.unary()
            if op == "/":
                if rhs == 0:
                    raise CalculationError("Cannot divide by zero")
                value /= rhs
            else:
                value *= rhs
        return value

    def unary(self) -> float:
        if self.peek() == "+":
            self.take()
            return self.unary()
        if self.peek() == "-":
            self.take()
            return -self.unary()
        if self.peek() == "√":
            self.take()
            value = self.unary()
            if value < 0:
                raise CalculationError("Square root of a negative number")
            return math.sqrt(value)
        return self.power()

    def power(self) -> float:
        value = self.postfix()
        if self.peek() == "^":
            self.take()
            exponent = self.unary()  # right associative, and permits negative exponents
            try:
                value = value ** exponent
            except (OverflowError, ValueError, ZeroDivisionError):
                raise CalculationError("Invalid power calculation") from None
            if isinstance(value, complex):
                raise CalculationError("Invalid power calculation")
        return float(value)

    def postfix(self) -> float:
        value = self.primary()
        while self.peek() == "%":
            self.take()
            value /= 100.0
        return value

    def primary(self) -> float:
        token = self.take()
        if token == "(":
            value = self.expression()
            if self.peek() != ")":
                raise CalculationError("Missing closing bracket")
            self.take()
            return value
        if token == ")":
            raise CalculationError("Unexpected closing bracket")
        try:
            return float(token)
        except ValueError:
            raise CalculationError("Invalid expression") from None


def evaluate(expression: str) -> float:
    """Evaluate calculator syntax without eval() or arbitrary code execution."""
    return _Parser(_tokenize(expression)).parse()


def format_result(value: float) -> str:
    """Render a finite number without distracting floating-point tails."""
    if not math.isfinite(value):
        raise CalculationError("Result is out of range")
    if abs(value) < 1e-12:
        value = 0.0
    if value.is_integer() and abs(value) < 1e16:
        return str(int(value))
    return f"{value:.12g}"
