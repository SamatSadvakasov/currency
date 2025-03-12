import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By

CURRENCIES = ('CNY', 'USD', 'EUR', 'RUB')

MIG_KZ_URL = 'https://mig.kz/'
KURS_KZ_URL = 'https://kurs.kz/'
CHINESE_WP_URL = 'https://i.jzj9999.com/quoteh5/?ivk_sa=1025883i'

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument("--disable-blink-features=AutomationControlled")

def get_soup_from_url(url):
    """Fetches and parses HTML content from a URL."""
    response = requests.get(url)
    return BeautifulSoup(response.text, "html.parser")

def parse_mig_kz():
    """Parses currency rates from mig.kz."""
    soup = get_soup_from_url(MIG_KZ_URL)
    buys = [float(d.text) for d in soup.find_all('td', 'buy delta-neutral')]
    sells = [float(d.text) for d in soup.find_all('td', 'sell delta-neutral')]
    currencies = [d.text for d in soup.find_all('td', 'currency')]
    rates = zip(currencies, buys, sells)
    return [rate for rate in rates if rate[0] in CURRENCIES]

def parse_kurs_kz():
    """Parses currency rates from kurs.kz using Selenium."""
    with webdriver.Chrome(options=options) as driver:
        driver.get(KURS_KZ_URL)
        time.sleep(2)
        select_element = driver.find_element(By.XPATH, '//*[@id="kurs-table"]/main/table/thead/tr/th[3]/span[2]/select')
        select = Select(select_element)
        results = []

        for currency in CURRENCIES:
            select.select_by_value(currency)
            time.sleep(0.5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            buy_rates = extract_rates(soup, f'{currency} - покупка')
            sell_rates = extract_rates(soup, f'{currency} - продажа')
            if buy_rates and sell_rates:
                results.append((currency, min(buy_rates), max(sell_rates)))

    return results

def extract_rates(soup, title):
    """Extracts rates from soup based on title."""
    rates = []
    for element in soup.find_all(title=title):
        try:
            rate = float(element.text)
            if rate > 0:
                rates.append(rate)
        except ValueError:
            continue
    return rates

def parse_chinese_wp() -> list:
    """Parses currency rates from the Chinese website."""
    with webdriver.Chrome(options=options) as driver:
        driver.get(CHINESE_WP_URL)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = [
            tuple(d.get_text(separator="\n", strip=True).split('\n')[:3])
            for d in soup.find_all('div', 'price-table-row')
        ]
        for rate in results:
            if rate[0] == '美元':
                return [('USD-CNY', float(rate[1]), float(rate[2]))]
    return []

