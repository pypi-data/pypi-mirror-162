# python packaging

[[pypi最小实现]](https://python-packaging.readthedocs.io/en/latest/minimal.html) [[本项目地址]](https://pypi.org/project/jiange/)

## 本地开发

```bash
# 本地开发环境
mkvirtualenv jiange -p /usr/bin/python3
```

## 本地测试

```bash
# 新建测试环境
mkvirtualenv test -p /usr/bin/python3
# 进入环境，并到包的工作目录下
cd /Users/zhanglinjian1/Documents/project/jiange
workon test
# 安装本包（修改后也可实时生效）
pip install -e .
```

## 上传到pypi

```bash
# 注册 & 生成 source distribution
python setup.py register sdist
# 上传至 pypi
twine upload dist/*
```
