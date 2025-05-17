import unittest

from scraper import price_to_float


class TestPriceToFloat(unittest.TestCase):
    def test_prices(self):
        test_cases = {
            "70 399 ₽": 70399.0,
            "78 194 ₽": 78194.0,
            "82 030": 82030.0,
            "1 234.56 ₽": 1234.56,
            "9 876,54 ₽": 9876.54,
        }

        for key, value in test_cases.items():
            with self.subTest(key):
                self.assertAlmostEqual(price_to_float(key), value)


if __name__ == '__main__':
    unittest.main()
