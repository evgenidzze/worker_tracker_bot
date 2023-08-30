import datetime
import calendar


def current_month_days_list():
    now = datetime.datetime.now()
    days_in_month = calendar.monthrange(now.year, now.month)[1]
    days_month_list = [f"{str(day).zfill(2)}.{now.strftime('%m')}" for day in range(1, days_in_month + 1)]
    return days_month_list

current_month_days_list()


lst_1 = ['ПІБ']
lst_1.extend(current_month_days_list())
