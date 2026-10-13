"""Testes inteiramente sintéticos; sem rede, banco, chaves ou serviços."""
import unittest

from mesa_sandbox.checkout import subtotal_cents


class SubtotalCentsTests(unittest.TestCase):
    def test_regular_subtotal(self):
        self.assertEqual(subtotal_cents(1250, 3), 3750)

    def test_zero_quantity(self):
        self.assertEqual(subtotal_cents(1250, 0), 0)

    def test_zero_price(self):
        self.assertEqual(subtotal_cents(0, 7), 0)

    def test_large_integer_exactness(self):
        self.assertEqual(subtotal_cents(10**12, 11), 11 * 10**12)

    def test_negative_values_are_rejected(self):
        for price, quantity in ((-1, 1), (1, -1)):
            with self.subTest(price=price, quantity=quantity):
                with self.assertRaises(ValueError):
                    subtotal_cents(price, quantity)

    def test_non_integer_and_boolean_values_are_rejected(self):
        for price, quantity in ((2.5, 1), ("2", 1), (True, 1), (1, False)):
            with self.subTest(price=price, quantity=quantity):
                with self.assertRaises(TypeError):
                    subtotal_cents(price, quantity)


if __name__ == "__main__":
    unittest.main()
