#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author: Linjian Zhang
Email: zhanglinjian1@corp.netease.com
Create Time: 2022/08/08 10:21:20

import os
import sys
PATH_PRJ = '/'.join(os.path.abspath(__file__).split('/')[:-2])
sys.path.append(PATH_PRJ)

## jieba

词性
import jieba.posseg as pseg
pairs = list(pseg.lcut('难过'))
list(list(pseg.lcut('分散'))[0])[1]  # 第一个词的词性
"""
import ahocorasick
import csv
import json
import re
import requests
import xlrd
import xlsxwriter
from os.path import exists


PAT_英文数字 = re.compile('[a-zA-Z0-9]')
PAT_标点 = re.compile(r'[\,\<\>\.\/\?\;\:\'\"\[\]\{\}\!\@\#\$\%\^\&\*\(\)\-\=\+\_\~，。、《》？；‘：”【】「」！￥…（）·\\\s]')
digit2traditional = {
    0: '零',
    1: '一',
    2: '二',
    3: '三',
    4: '四',
    5: '五',
    6: '六',
    7: '七',
    8: '八',
    9: '九',
    10: '十',
    11: '十一',
    12: '十二',
    13: '十三',
    14: '十四',
    15: '十五',
    16: '十六',
    17: '十七',
    18: '十八',
    19: '十九',
    20: '二十'
}


def call_api(prefix, body=None, postfix=None, timeout=10):
    """访问 post / get 接口

    Args:
        prefix (str):
            请求的 url
        method (str):
            post / get
        body (dict):
            request，没有 body 的情况下，默认为 get 请求
        postfix (str):
            get 请求时，如果 url 后缀包含中文，则放此字段中进行另外编码拼接
        timeout (int):
            超时时间，秒级别

    Return:
        (dict): response，如果获取数据失败，则返回空字典

    Examples:
        >>> call_api(prefix='http://localhost:80/post', body={'k': 'v'})
        >>> call_api(prefix='http://localhost:80/get')
        >>> call_api(prefix='http://localhost:80/get', postfix='姚明', method='get')
    """
    res = "{}"
    if body:
        try:
            res = requests.post(prefix, json=body, timeout=timeout)
            res = res.text
        except Exception:
            pass
    else:
        if postfix:
            prefix += requests.utils.quote(postfix)
        try:
            res = requests.get(prefix, timeout=timeout).text
        except Exception:
            pass
    return load_json(res)


'''markdown'''


def print_md_title(title):
    lines = []
    lines.append(' | '.join(title))
    lines.append('|'.join(['---']*len(title)))
    string = '\n'.join(lines)
    print(string)


def load_line(path_src, max_num=0, with_filter=False):
    """按行读取句子

    Args:
        path_src (str): 源文件路径
        max_num (int): 返回行数，默认 0 表示全部返回
        with_filter (bool): 是否要过滤换行等符号，默认不过滤
    """
    data = []
    cnt = 0
    with open(path_src, 'r', encoding='utf8') as f:
        for line in f.readlines():
            if max_num > 0 and cnt > max_num:
                break
            line = line.strip()
            if not line:
                continue

            if with_filter is True:
                line = line.replace(' ', '').replace('\t', '')
            data.append(line)
            cnt += 1
    return data


def save_line(data, path_tgt, has_n=False):
    """按行保存句子

    Args:
        data (list): 要保存的句子
        path_tgt (str): 目标文件路径
        has_n (bool): 每个句子末尾是否包含了换行符，默认没有
    """
    with open(path_tgt, 'w', encoding='utf8') as f:
        if has_n is True:
            for item in data:
                f.writelines(f'{item}')
        else:
            for item in data:
                f.writelines(f'{item}\n')


'''json'''


def load_json(data):
    return json.loads(data)


def print_json(data):
    # `data` supports string and dict
    if isinstance(data, dict) or isinstance(data, list):
        pass
    elif isinstance(data, str):
        data = load_json(data)
    else:
        raise ValueError(f'only support dict or str data, but given {type(data)}')
    print(dump_json(data))


def dump_json(data, indent=True):
    if indent is True:
        return json.dumps(data, ensure_ascii=False, indent=4)
    return json.dumps(data, ensure_ascii=False)


def load_json_file(path_src):
    if not exists(path_src):
        raise FileExistsError(f'error: file not exist, path: {path_src}')
    with open(path_src, 'r', encoding='utf8') as f:
        data = json.load(f)
    return data


def load_json_list_file(path_src):
    if not exists(path_src):
        raise FileExistsError(f'error: file not exist, path: {path_src}')
    data = list()
    with open(path_src, 'r', encoding='utf8') as f:
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            data.append(json.loads(line))
    return data


def save_json_file(data, path_tgt, indent=False):
    with open(path_tgt, 'w', encoding='utf8') as f:
        if indent is True:
            json.dump(data, f, ensure_ascii=False, indent=4)
        else:
            json.dump(data, f, ensure_ascii=False)


def save_json_list_file(data, path_tgt):
    """保存 json 至文件，一行一个 json-string"""
    with open(path_tgt, 'w', encoding='utf8') as f:
        for item in data:
            json.dump(item, f, ensure_ascii=False)
            f.write('\n')


'''excel'''


def load_wb(path_src):
    """
    - sheets()
    st = wb.sheets()[0]
    nrows = st.nrows
    first_row = st.row_values(0)

    - sheet_by_name()
    wb.sheet_by_name('sheetname')
    """
    return xlrd.open_workbook(path_src)


def load_wb_list(path_src, sheet_name=None, return_title=False, escape_first=False):
    """默认返回 excel 的第一个数据表，双重列表形式

    Args:
        path_src (str): 源文件路径
        sheet_name (str): sheet 名，如果不指定，则返回 sheet 0 的数据
        return_title (bool): 是否返回标题（第一行数据认为是标题），默认不返回
        escape_first (bool): 是否跳过首行，也即从第二行开始读取数据，此时标题则为第二行

    Return:
        (list[list]): 数据的双重列表
        (list, optional): 标题，return_title 为 True 时才会返回
    """
    wb = load_wb(path_src)
    if sheet_name:
        st = wb.sheet_by_name(sheet_name)
    else:
        st = wb.sheets()[0]
    nrows = st.nrows
    ret = []
    title = []

    start_id = 0
    if escape_first is True:
        start_id = 1
    for i in range(start_id, nrows):
        row = st.row_values(i)
        row = [pre_process_int(x) for x in row]
        if i == start_id:
            if return_title is True:
                title = row
            else:
                ret.append(row)
        else:
            ret.append(row)
    if return_title is True:
        return ret, title
    else:
        return ret


def save_wb(data, path_tgt, st_name='default', title=None):
    """保存数据至 xlsx 的 sheet 中

    Args:
        data (list[list]): 要存储的数据，双重列表
        path_tgt (str):
        st_name (str, optional):
        title (list, optional): 如果没有给定，则 data 从第一行开始存储
    """
    wb = xlsxwriter.Workbook(path_tgt)
    st = wb.add_worksheet(st_name)
    if title:
        for i, item in enumerate(title):
            st.write(0, i, item)
        start_id = 1
    else:
        start_id = 0

    for i, row_values in enumerate(data):
        for j, item in enumerate(row_values):
            st.write(i+start_id, j, str(item))
    wb.close()


'''csv'''


def load_csv_list(path_src, return_title=False):
    """

    Args:
        path_src (str): 源文件路径
        return_title (bool): 是否返回标题（第一行数据认为是标题），默认不返回
    Return:
        (list[list]): 数据的双重列表
        (list, optional): 标题，return_title 为 True 时才会返回
    """
    title = None
    with open(path_src, mode='r', encoding='utf-8-sig') as f:
        csv_reader = csv.reader(f, delimiter=',')
        data = []
        for i, row in enumerate(csv_reader):
            if i == 0:
                title = [x.strip() for x in row]
                continue
            data.append([x.strip() for x in row])
    if return_title is True:
        return data, title
    return data


def save_csv_list(data, path_tgt, title):
    """将双重列表写入 csv 文件

    Args:
        data (list[list[str]]): [ [1 2 3] [4 5 6] ]
        path_tgt (str):
        title (list[str]): [ key1, key2, key3 ]
    """
    with open(path_tgt, mode='w', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(title)
        for item in data:
            writer.writerow(item)


'''ac'''


def get_ac(word_list, info_list=None):
    """

    Args:
        word_list (list): 用于建索引
        info_list (list): 如果值为空，则默认把索引自身作为内容填进去；如果不为空，需要和 word_list 一一对应
    Returns:
        ac instance: usage example `list(ac.iter(string))`  # [(position, info)]
    """
    ac = ahocorasick.Automaton()

    if info_list:
        assert len(word_list) == len(info_list), 'word_list 和 info_list 的长度必须一至'
        for word, info in zip(word_list, info_list):
            ac.add_word(word, info)  # (index, info)
    else:
        for word in word_list:
            ac.add_word(word, word)  # (index, info)

    ac.make_automaton()
    return ac


def judge_ac(ac, string):
    """如果 string 出现在 ac 中，则返回 true"""
    ret = list(ac.iter(string))
    if not ret:
        return False
    ret.sort(key=lambda x: len(x[1]))  # [(position, info)]
    return ret[-1][1] == string


def pre_process_int(x):
    try:
        x = float(x)
    except Exception:
        return x

    # string 类型的数据已经返回，到这一步只可能是 float/int 数据，e.g. 1.0, 1.1
    y = int(x)
    if y == x:
        return str(y)
    else:
        return str(x)


if __name__ == '__main__':
    print()