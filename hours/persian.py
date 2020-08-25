# coding: utf-8
from __future__ import unicode_literals
import calendar
import datetime

maketrans = lambda A, B: dict((ord(a), b) for a, b in zip(A, B))
en_numbers = maketrans('1234567890', '۱۲۳۴۵۶۷۸۹۰')
numbers = maketrans('۱۲۳۴۵۶۷۸۹۰', '1234567890')
normalize_digits = lambda text: text.translate(numbers)
persian_numbers = lambda text: text.translate(en_numbers)


def get_weekday_count(start, end, weekday):
    """
    this function returns the number of specified weekday between start + 1 and end.
        so we must find the day before start first
    :param start: start date
    :param end: end date
    :param weekday: weekday name
    :return: number of specified weekday
    """
    the_day = datetime.date(*map(int, start.split('-')))
    prev_day = the_day - datetime.timedelta(days=1)
    start = prev_day.strftime('%Y-%m-%d')
    start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
    end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
    count = 0
    for i in range((end_date - start_date).days):
        day = calendar.day_name[(start_date + datetime.timedelta(days=i + 1)).weekday()]
        if day.lower() == weekday.lower():
            count += 1
    return count


def get_days_count(start, end):
    """
    get days count between two dates
    """
    date_format = "%Y-%m-%d"
    start = datetime.datetime.strptime(start, date_format)
    end = datetime.datetime.strptime(end, date_format)
    delta = end - start
    return delta.days + 1