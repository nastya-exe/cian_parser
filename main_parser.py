import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from db_rrequests import find_active_ads, save_info_db, change_status_active, data_change
from config import url_studios
from functions import datetime_of_publication, payment_upon_entry


def parser(driver, url):
    driver.get(url)

    # Сбор ссылок на объявления с первой страницы
    links_one = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'media')]"))
    )

    hrefs = []
    for link in links_one:
        try:
            href = link.get_attribute("href")
            if href:
                hrefs.append(href)
        except StaleElementReferenceException:
            continue

    # Сбор ссылок на объявления со второй страницы
    second_page = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@rel='noopener' and span[text()='2']]"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", second_page)
    second_page.click()
    time.sleep(2)

    links_second = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, "//a[contains(@class, 'media')]"))
    )

    for link in links_second:
        try:
            href = link.get_attribute("href")
            if href:
                hrefs.append(href)
        except StaleElementReferenceException:
            continue

    active_ads = find_active_ads()

    for href in hrefs:
        # Добавление новых объявлений в бд
        if href not in active_ads:
            driver.get(href)

            # Название объявления
            name = driver.find_element(By.CSS_SELECTOR, "div[data-name='OfferTitleNew'] h1")

            # Цена и оплата при заселении
            price = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='price-amount'] span"))
            )
            price_int = int(('').join(price.text[:6].split()))
            payment_info = driver.find_elements(By.CSS_SELECTOR, "div[data-name='OfferFactItem'] span")
            payment = payment_upon_entry(payment_info[3].text, payment_info[5].text, payment_info[7].text, price_int)

            # Название ближайшего метро, время до не него, тип передвижения
            underground_items = driver.find_elements(By.CSS_SELECTOR, "li[data-name='UndergroundItem']")

            name_metro = underground_items[0].find_element(By.CSS_SELECTOR, "a")
            time_elem = underground_items[0].find_element(By.CSS_SELECTOR,
                                                          "span[data-name='UndergroundTime'], span[class*='underground_time']")
            time_elem_int = int(time_elem.text.split(' ')[0])

            svg_elem = time_elem.find_element(By.TAG_NAME, "svg")
            paths = svg_elem.find_element(By.TAG_NAME, "path")
            icon_type = "на машине" if paths.get_attribute("fill-rule") == "evenodd" else "пешком"

            # Время последнего обновления объявления
            last_update = (driver.find_elements(By.CSS_SELECTOR, "div[data-testid='metadata-updated-date'] span"))[0]
            date_time_obj = datetime_of_publication(last_update.text)

            save_info_db(name.text, price_int, name_metro.text, href, date_time_obj, payment, time_elem_int, icon_type)


# Обновление данных в бд в 15:00 и 20:00
def update_add(driver, hrefs):
    time_now = datetime.now().time().strftime("%H:%M")

    if '14:50' <= time_now < '15:00' or '20:50' <= time_now < '20:10':

        for href in hrefs:
            driver.get(href)

            try:
                price = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='price-amount'] span"))
                )
                last_update = (driver.find_elements(By.CSS_SELECTOR, "div[data-testid='metadata-updated-date'] span"))[
                    0]
                payment_info = driver.find_elements(By.CSS_SELECTOR, "div[data-name='OfferFactItem'] span")

                date_time_obj = datetime_of_publication(last_update.text)
                price_int = int(('').join(price.text[:6].split()))
                payment = payment_upon_entry(payment_info[3].text, payment_info[5].text, payment_info[7].text,
                                             price_int)

                data_change(price_int, href, date_time_obj, payment)

            except (TimeoutException, NoSuchElementException):
                change_status_active(href)


def start(url):
    while True:
        driver = webdriver.Chrome()
        update_add(driver, find_active_ads())
        parser(driver, url)
        driver.quit()
        time.sleep(600)


start(url_studios)
