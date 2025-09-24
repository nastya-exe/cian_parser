from datetime import date, datetime, timedelta


# Форматирование даты обновления объявления
def datetime_of_publication(last_update):
    today = date.today()
    year_now = today.year
    info_upd = last_update.split(', ')
    months = {
        'янв': 1, 'фев': 2, 'мар': 3, 'апр': 4, 'май': 5, 'июн': 6,
        'июл': 7, 'авг': 8, 'сен': 9, 'окт': 10, 'ноя': 11, 'дек': 12
    }

    if 'сегодня' in last_update:
        date_time = f'{today} {info_upd[1]}'
        date_time_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
    elif 'вчера' in last_update:
        yesterday = today - timedelta(days=1)
        date_time = f'{yesterday} {info_upd[1]}'
        date_time_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M")
    else:
        date_str = info_upd[0].split(': ')[1]
        month = months[date_str.split(' ')[1]]
        day = date_str.split(' ')[0]

        date_time = f'{year_now}-{month}-{day} {info_upd[1]}'

        date_time_obj = datetime.strptime(date_time, "%Y-%m-%d %H:%M")

    return date_time_obj


# Подсчет оплаты при заселении
def payment_upon_entry(deposit, commission, prepayment, price):
    new_deposit = int((deposit.replace(" ", "")).replace("₽", "")) if deposit != 'нет' else 0
    percent_commission = int(commission.replace("%", "")) if commission != 'нет' else 0
    new_prepayment = int(prepayment.split(' ')[0]) if prepayment != 'нет' else 0

    all_summ = round(new_deposit + price * percent_commission / 100 + price * new_prepayment)

    return all_summ


if __name__ == '__main__':
    payment_upon_entry('40 000 ₽', '70%', '1 месяц', 40000)
    payment_upon_entry('49 000 ₽', 'нет', '1 месяц', 45000)
