"""Regression tests for the safe arithmetic parser. Run: python -m unittest -v"""
import unittest

from calculator import CalculationError, evaluate, format_result


class CalculatorTests(unittest.TestCase):
    def test_basic_operations(self):
        self.assertEqual(evaluate("2+3"), 5)
        self.assertEqual(evaluate("9−4"), 5)
        self.assertEqual(evaluate("6×7"), 42)
        self.assertEqual(evaluate("8÷2"), 4)

    def test_decimal_and_precision(self):
        self.assertEqual(format_result(evaluate("0.1+0.2")), "0.3")
        self.assertEqual(evaluate("1.25×4"), 5)

    def test_precedence_and_brackets(self):
        self.assertEqual(evaluate("2+3×4"), 14)
        self.assertEqual(evaluate("(2+3)×4"), 20)
        self.assertEqual(evaluate("2^3^2"), 512)

    def test_negative_and_power(self):
        self.assertEqual(evaluate("−5+2"), -3)
        self.assertEqual(evaluate("2^−2"), 0.25)
        self.assertEqual(evaluate("−2^2"), -4)

    def test_percentage_square_root(self):
        self.assertEqual(evaluate("25%"), 0.25)
        self.assertEqual(evaluate("√9"), 3)
        self.assertEqual(evaluate("5^2"), 25)

    def test_errors(self):
        for expression in ("1/0", "1÷0"):
            with self.subTest(expression=expression), self.assertRaises(CalculationError):
                evaluate(expression)
        for expression in ("2+", "(2+3", "2+*3", "√−4", "__import__('os')"):
            with self.subTest(expression=expression), self.assertRaises(CalculationError):
                evaluate(expression)


if __name__ == "__main__":
    unittest.main()
