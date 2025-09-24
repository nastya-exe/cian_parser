import os
from dotenv import load_dotenv

load_dotenv()

database_url = os.getenv('url_db')
bot_token = os.getenv('bot_token')
url_studios = 'https://www.cian.ru/cat.php?currency=2&deal_type=rent&engine_version=2&foot_min=20&maxprice=50000&offer_type=flat&only_foot=-2&region=1&room9=1&type=4'