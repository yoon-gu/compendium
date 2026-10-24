import unittest

from cart.pricing import apply_coupon, shipping_for


class TestPricing(unittest.TestCase):
    def test_free_shipping(self):
        self.assertEqual(shipping_for(60_000), 0)

    def test_percent_coupon(self):
        self.assertEqual(apply_coupon(10_000, {"type": "percent", "value": 10}), 9_000)


if __name__ == "__main__":
    unittest.main()
