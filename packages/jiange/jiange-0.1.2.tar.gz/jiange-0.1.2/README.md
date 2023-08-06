# python packaging

https://python-packaging.readthedocs.io/en/latest/minimal.html

## 本地测试

```bash
# 新建虚拟环境
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
python setup.py register sdist upload
# 
twine upload dist/*
```

- python setup.py sdist
- 上传到 pypi：twine upload dist/*
