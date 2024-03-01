from playwright.sync_api import sync_playwright
from datetime import datetime

URL = 'https://www.cbr.ru/currency_base/daily/'


def get_exchange_rates():
    """Получение данных о курсах валют с сайта ЦБ."""

    currencies = {}

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(URL)
        date = page.locator('.datepicker-filter_button').inner_text()
        all_currencies_data = page.get_by_role('row').all_inner_texts()

        for row in all_currencies_data[1:]:
            currency = row.split('\t')
            currencies[currency[1]] = currency[2:]

        last_update = datetime.now().timestamp()

    return date, currencies, last_update
