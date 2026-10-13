"""Testes inteiramente sintéticos; sem rede, banco, chaves ou serviços."""
import unittest

from mesa_sandbox.checkout import apply_discount_cents, subtotal_cents


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


class DiscountCentsTests(unittest.TestCase):
    def test_percentage_discount(self):
        self.assertEqual(apply_discount_cents(5000, 1500), 4250)

    def test_fractional_cent_is_rounded_down(self):
        self.assertEqual(apply_discount_cents(10001, 2500), 7500)

    def test_no_discount(self):
        self.assertEqual(apply_discount_cents(1900, 0), 1900)

    def test_full_discount(self):
        self.assertEqual(apply_discount_cents(1900, 10000), 0)

    def test_zero_subtotal(self):
        self.assertEqual(apply_discount_cents(0, 5200), 0)

    def test_large_integer_exactness(self):
        self.assertEqual(apply_discount_cents(10**16, 100), 99 * 10**14)

    def test_out_of_range_or_negative_values(self):
        for subtotal, points in ((-1, 0), (50, -1), (50, 10001)):
            with self.subTest(subtotal=subtotal, points=points):
                with self.assertRaises(ValueError):
                    apply_discount_cents(subtotal, points)

    def test_non_integer_and_boolean_values_are_rejected(self):
        for subtotal, points in ((12.5, 1), ("12", 1), (True, 1), (1, False)):
            with self.subTest(subtotal=subtotal, points=points):
                with self.assertRaises(TypeError):
                    apply_discount_cents(subtotal, points)


if __name__ == "__main__":
    unittest.main()
