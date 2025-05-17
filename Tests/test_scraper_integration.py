import unittest

from scraper import Scraper


class TestScraperIntegration(unittest.TestCase):
    def test_get_price_real_site(self):
        url = "https://www.oldi.ru/catalog/element/02057286/"
        xpath = '//span[@class="price_leg add-rub"]'
        price = Scraper.get_price(url, xpath)
        self.assertIsInstance(price, float)
        self.assertGreater(price, 0)


if __name__ == "__main__":
    unittest.main()
