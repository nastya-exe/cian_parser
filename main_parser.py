import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from db_rrequests import find_active_ads, save_info_db

def parser(driver, url):
    driver.get(url)

    links = driver.find_elements(By.XPATH, "//a[contains(@class, 'media')]")

    hrefs = [link.get_attribute("href") for link in links[:6]]
    info = {}
    active_ads = find_active_ads()

    for href in hrefs:
        if href not in active_ads:
            try:
                driver.get(href)

                price = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='price-amount'] span"))
                )
                name = driver.find_element(By.CSS_SELECTOR, "div[data-name='OfferTitleNew'] h1")
                name_metro = driver.find_element(By.CSS_SELECTOR, "li[data-name='UndergroundItem'] a")
                url_photo = driver.find_element(By.CSS_SELECTOR, "div[data-name='GalleryInnerComponent'] img")

                first_url = url_photo.get_attribute("src")
                price_int = int(('').join(price.text[:6].split()))

                info[href] = {'name':name.text, 'price': price_int,
                              'name_metro':name_metro.text, 'url_photo':first_url}
                save_info_db(name.text, price_int, name_metro.text, first_url, href)

            except Exception:
                print(f'Страница {href} была удалена')

    print(info)

def start(url):
    driver = webdriver.Chrome()
    while True:
        parser(driver, url)
        time.sleep(600)

url_studios = 'https://www.cian.ru/cat.php?currency=2&deal_type=rent&engine_version=2&foot_min=20&maxprice=50000&offer_type=flat&only_foot=-2&region=1&room9=1&type=4'
parser(url_studios)