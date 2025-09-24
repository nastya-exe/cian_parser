import sqlite3
from config import database_url


# Добавление объявления в бд
def save_info_db(ad, price, name_metro, link, date_add, payment):
    db = sqlite3.connect(database_url)
    cursor = db.cursor()

    cursor.execute("""
        INSERT INTO info_studios(name, price, name_metro, link, date_add, payment)
        VALUES(?, ?, ?, ?, ?, ?)
        ON CONFLICT(link) DO UPDATE SET
            name=excluded.name,
            price=excluded.price,
            name_metro=excluded.name_metro,
            date_add=excluded.date_add,
            payment=excluded.payment
    """, (ad, price, name_metro, link, date_add, payment))

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
    """, (link,))

    db.commit()
    db.close()


# Изменение данных объявления
def data_change(price_new, link, date_new, payment_new):
    db = sqlite3.connect(database_url)
    cursor = db.cursor()

    cursor.execute("""
        UPDATE info_studios
        SET price = ?, date_add = ?, payment = ?
        WHERE link = ?
    """, (price_new, date_new, payment_new, link))

    db.commit()
    db.close()


# Объявления за последние hours
def find_ads(hour):
    db = sqlite3.connect(database_url)
    cursor = db.cursor()

    cursor.execute(f"""
		SELECT name, price, name_metro, link, date_add, payment
		FROM info_studios
		WHERE DATETIME(date_add) >= DATETIME('now', '-{hour} hour', '+3 hour')
		ORDER BY date_add
    """)

    rows = [list(row) for row in cursor.fetchall()]
    db.close()
    return rows


# Объявления за сегодняшний день
def find_ads_today():
    db = sqlite3.connect(database_url)
    cursor = db.cursor()

    cursor.execute("""
        SELECT name, price, name_metro, link, date_add, payment
        FROM info_studios
        WHERE DATE(date_add) = DATE('now')
        ORDER BY date_add DESC
    """)

    rows = [list(row) for row in cursor.fetchall()]
    db.close()
    return rows
