import concurrent.futures
import pandas as pd

from scraper import Scraper


def fetch_prices(df: pd.DataFrame) -> list:

    def fetch_price(row):
        price = Scraper.get_price(row['url'], row['xpath'])
        return price

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        prices = list(executor.map(fetch_price, [row for _, row in df.iterrows()]))
        #prices = [70399.0, 29999.0, None, None, 31770.0, 70399.0, 82030.0, None]

    return prices

def formatting_to_print(df: pd.DataFrame) -> pd.DataFrame:
    MAX_TITLE_LEN = 25

    def shorten_url(url):
        if url:
            return url.split('/')[2].replace('www.', '')
        return url

    def shorten_text(text, max_len):
        if len(text) > max_len:
            return text[:max_len - 3] + '...'
        return text

    titles = []
    urls = []
    xpath_flags = []

    for _, row in df.iterrows():
        title = shorten_text(row['title'], MAX_TITLE_LEN) if pd.notna(row['title']) and row['title'].strip() != '' else '-'
        titles.append(title)

        url = shorten_url(row['url']) if pd.notna(row['url']) and row['url'].strip() != '' else '-'
        urls.append(url)

        xpath_flag = '[xpath]' if pd.notna(row['xpath']) and row['xpath'].strip() != '' else '-'
        xpath_flags.append(xpath_flag)

    return pd.DataFrame({
        'title': titles,
        'url': urls,
        'xpath': xpath_flags
    })



