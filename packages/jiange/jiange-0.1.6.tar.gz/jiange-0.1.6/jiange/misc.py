#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Linjian Zhang
Email: zhanglinjian1@corp.netease.com
Create Time: 2022/08/08 11:22:26
"""
from collections import OrderedDict
import random


def shuffle_two_list(a, b):
    c = list(zip(a, b))
    random.shuffle(c)
    a, b = zip(*c)
    return a, b


def is_chinese_char(c):
    cp = ord(c)
    if (0x4E00 <= cp <= 0x9FFF) or \
            (0x3400 <= cp <= 0x4DBF) or \
            (0x20000 <= cp <= 0x2A6DF) or \
            (0x2A700 <= cp <= 0x2B73F) or \
            (0x2B740 <= cp <= 0x2B81F) or \
            (0x2B820 <= cp <= 0x2CEAF) or \
            (0xF900 <= cp <= 0xFAFF) or \
            (0x2F800 <= cp <= 0x2FA1F):
        return True
    return False


def is_chinese_sentence(s, p=1.0):
    """

    Args:
        s (str):
        p (float): 阈值，0 ~ 1 之间，1 表示全为中文，0表示不判断，也即永远为 True
    Returns:
        bool: flag
    """
    if not isinstance(s, str):
        return False

    s = s.strip()
    if not s:
        return False

    x = [int(is_chinese_char(x)) for x in s]
    x = sum(x) / len(s)
    return x >= p


class LimitedSizeDict(OrderedDict):
    """先进先出
    reference: https://stackoverflow.com/questions/2437617/how-to-limit-the-size-of-a-dictionary/2437645#2437645

    Examples:
        >>> d = LimitedSizeDict(size_limit=10)
        >>> d[1] = 2

    """
    def __init__(self, *args, **kwargs):
        self.size_limit = kwargs.pop('size_limit', None)
        OrderedDict.__init__(self, *args, **kwargs)
        self._check_size_limit()

    def __setitem__(self, key, value):
        OrderedDict.__setitem__(self, key, value)
        self._check_size_limit()

    def _check_size_limit(self):
        if self.size_limit is not None:
            while len(self) > self.size_limit:
                self.popitem(last=False)


if __name__ == '__main__':
    print('misc')