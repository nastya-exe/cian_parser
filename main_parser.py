import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from db_rrequests import find_active_ads, save_info_db, change_status_active, data_change
from config import url_studios
from functions import datetime_of_publication, payment_upon_entry, determine_time


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
        except:
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
        except:
            continue

    active_ads = find_active_ads()

    for href in hrefs:
        # Добавление новых объявлений в бд
        if href not in active_ads:
            driver.get(href)

            price = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='price-amount'] span"))
            )
            name = driver.find_element(By.CSS_SELECTOR, "div[data-name='OfferTitleNew'] h1")
            name_metro = driver.find_element(By.CSS_SELECTOR, "li[data-name='UndergroundItem'] a")
            last_update = (driver.find_elements(By.CSS_SELECTOR, "div[data-testid='metadata-updated-date'] span"))[0]
            payment_info = driver.find_elements(By.CSS_SELECTOR, "div[data-name='OfferFactItem'] span")

            date_time_obj = datetime_of_publication(last_update.text)

            price_int = int(('').join(price.text[:6].split()))
            payment = payment_upon_entry(payment_info[3].text, payment_info[5].text, payment_info[7].text, price_int)

            save_info_db(name.text, price_int, name_metro.text, href, date_time_obj, payment)

    # Обновление данных в бд в 15:00 и 20:00
    if determine_time():
        hrefs = find_active_ads()
        for href in hrefs:
            driver.get(href)

            try:
                price = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='price-amount'] span"))
                )
                last_update = (driver.find_elements(By.CSS_SELECTOR, "div[data-testid='metadata-updated-date'] span"))[0]
                payment_info = driver.find_elements(By.CSS_SELECTOR, "div[data-name='OfferFactItem'] span")

                date_time_obj = datetime_of_publication(last_update.text)
                price_int = int(('').join(price.text[:6].split()))
                payment = payment_upon_entry(payment_info[3].text, payment_info[5].text, payment_info[7].text,
                                             price_int)

                data_change(price_int, href, date_time_obj, payment)

            except:
                change_status_active(href)


def start(url):
    driver = webdriver.Chrome()
    while True:
        parser(driver, url)
        time.sleep(600)


start(url_studios)
