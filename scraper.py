import time
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def price_to_float(price_str: str) -> float:
    cleaned = ''.join(ch for ch in price_str if ch.isdigit() or ch in ',.')
    cleaned = cleaned.replace(',', '.')
    return float(cleaned)

class Scraper:
    """
    Static class to scrape an information from web-page.
    """

    def __new__(cls, *args, **kwargs):
        raise TypeError(f"Cannot instantiate class {cls.__name__}")

    @staticmethod
    def __create_driver() -> webdriver.Chrome:
        """
        Creates and returns a driver for scraping.

        :return: Chrome webdriver.
        """

        # set settings for a driver
        options = Options()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " \
                     "Chrome/115.0 Safari/537.36"
        options.add_argument(f'user-agent={user_agent}')
        options.add_argument("start-maximized")
        options.add_argument("disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--headless")

        driver = webdriver.Chrome(options=options)

        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                """
        })

        return driver

    @staticmethod
    def get_price(url: str, xpath: str) -> float:
        price = None

        driver = Scraper.__create_driver()
        driver.get(url)

        time.sleep(5)

        wait = WebDriverWait(driver, 10)
        try:
            price_text = wait.until(EC.presence_of_element_located((By.XPATH, xpath))).text
            price = price_to_float(price_text)
        except (selenium.common.exceptions.TimeoutException, selenium.common.exceptions.NoSuchElementException) as ex:
            print(f'Exception in Scraper: {ex}')
        finally:
            driver.quit()
            return price
