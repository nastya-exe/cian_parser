import sqlite3
from config import database_url


# Добавление объявления в бд
def save_info_db(name, price, name_metro, url_photo, link):
    db = sqlite3.connect(database_url)
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO info_studios(name, price, name_metro, url_photo, link)
        VALUES(?, ?, ?, ?, ?)
    """, (name, price, name_metro, url_photo, link))

    db.commit()
    db.close()


# Список из всех активных ссылок
def find_active_ads():
    db = sqlite3.connect(database_url)
    cursor = db.cursor()

    cursor.execute("""
        SELECT link FROM info_studios
        WHERE active = TRUE
    """)

    rows = [row[0] for row in cursor.fetchall()]
    db.close()

    return rows


# Изменение статуса активности объявления
def change_status_active(link):
    db = sqlite3.connect(database_url)
    cursor = db.cursor()

    cursor.execute("""
        UPDATE info_studios
        SET active = FALSE
        WHERE link = ?
    """, link)

    db.commit()
    db.close()
