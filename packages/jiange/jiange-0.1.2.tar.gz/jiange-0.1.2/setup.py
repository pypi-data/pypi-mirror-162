from setuptools import setup


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


install_requires = load_line('requirements.txt')


setup(
    name='jiange',
    version='0.1.2',
    description='functions to save your life',
    url='http://github.com/linjian',
    author='Zhang Linjian',
    author_email='zhanglinjian1@gmail.com',
    license='MIT',
    packages=['jiange'],
    install_requires=install_requires,
    zip_safe=False)
