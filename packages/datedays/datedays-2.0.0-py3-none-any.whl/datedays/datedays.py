"""
@time: 2022/8/5 15:00
@description
日期工具，主要用于获取以下格式日期的列表
['2022-08-05', '2022-08-06', '2022-08-07'，***]
以此类推

Get the list of days in the format "%y-%m-%d"
When we want a lot of time
For example: ['2022-08-05','2022-08-06','2022-08-07', * * *]
This library can be used for this fixed format date array
"""

__author__ = 'liang1024'
__email__ = "11751155@qq.com"

import calendar
import time
from datetime import date

from dateutil.relativedelta import relativedelta


def getmore(number=3):
    '''
    获取所需日期数量列表，默认3个月内
    Get the required date quantity list, within 3 months by default
    :param number: 生成的月数 Number of months generated
    :return: list
    '''
    days_list = getcurrent_monthsurplusday()
    for i in range(1, number + 1):
        days_list += getnextmonth_surplusday(next_months=i)
    return days_list


def getcurrent_monthsurplusday(current_date=None):
    '''
    获取指定月的剩余天数，
    current_date为空时，则获取本月剩余天数
    Get the remaining days of the specified month,
    current_ If the date is empty,
    the current remaining days will be obtained
    :param current_date:'%Y-%m-%d'
    :return: list
    '''
    if not current_date:
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    c_list = []
    c_times = current_date.split('-')
    c_year = int(c_times[0])
    c_month = int(c_times[1])
    c_day = int(c_times[2])
    monthrange = calendar.monthrange(c_year, c_month)
    for c_day in [i for i in range(c_day, monthrange[1] + 1)]:  # +1
        s_day = c_day
        s_month = c_month
        if c_day < 10:
            s_day = '0' + str(c_day)
        if c_month < 10:
            s_month = '0' + str(c_month)
        s_date = f'{c_year}-{s_month}-{s_day}'
        c_list.append(s_date)
    return c_list


def getnextmonth_surplusday(current_date=None, next_months=1):
    '''
    返回下个月日期列表 (自动跨年)
    Return to the next month date list (automatically cross year)
    :param current_date:指定月份 Specified month '%Y-%m-%d'
    :param next_months: 指定月份的间隔 Specify the interval of the month
    :return: list
    '''
    if not current_date:
        current_date = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    n_list = []
    c_times = current_date.split('-')
    c_year = int(c_times[0])
    c_month = int(c_times[1])
    next_date = date(c_year, c_month, 1) + relativedelta(months=+next_months)
    n_year = next_date.year
    n_month = next_date.month
    n_monthrange = calendar.monthrange(n_year, n_month)
    for c_day in [i for i in range(1, n_monthrange[1] + 1)]:
        s_day = c_day
        s_month = n_month
        if c_day < 10:
            s_day = '0' + str(c_day)
        if n_month < 10:
            s_month = '0' + str(n_month)
        s_date = f'{n_year}-{s_month}-{s_day}'
        n_list.append(s_date)
    return n_list


'''
测试/test
print(getmore())
print(getcurrent_monthsurplusday('2023-08-05'))
print(getnextmonth_surplusday())
'''
