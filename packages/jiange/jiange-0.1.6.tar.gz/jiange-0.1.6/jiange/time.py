#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Linjian Zhang
Email: zhanglinjian1@corp.netease.com
Create Time: 2022/08/08 11:16:46
"""
import datetime
import time


def get_time():
    """返回时间 [19, 24, 2] 时分秒"""
    t = time.localtime(time.time())  # year, month, day, hour, minute, second
    return [t[3], t[4], t[5]]


def get_time_string():
    """返回当前详细时间 2021-05-11 14:46"""
    t = time.localtime(time.time())  # year, month, day, hour, minute, second
    string = f'{t[0]}-{t[1]:02d}-{t[2]:02d} {t[3]:02d}:{t[4]:02d}'
    return string


def get_date(delta=0):
    """返回日期: [2021, 5, 10, '一'] 年 月 日 星期

    Args:
        delta (int): 0 今天 / -1 昨天 / 1 明天
    Returns:
        (list)
    """
    today = datetime.date.today()
    if delta != 0:
        day_delta = datetime.timedelta(days=delta)
        today = today + day_delta

    id2week = {
        0: '一',
        1: '二',
        2: '三',
        3: '四',
        4: '五',
        5: '六',
        6: '日'
    }
    return [today.year, today.month, today.day, id2week[today.weekday()]]


def get_interval_days(year, month, day):
    # 计算给定的日期和当天日期的间隔天数，间隔分钟
    year0, month0, day0, week0 = get_date()
    d1 = datetime.datetime(year0, month0, day0)
    d2 = datetime.datetime(year, month, day)
    return (d1 - d2).days


if __name__ == '__main__':
    print('time')