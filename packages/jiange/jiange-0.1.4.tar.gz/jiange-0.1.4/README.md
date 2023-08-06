# python packaging

[[pypi最小实现]](https://python-packaging.readthedocs.io/en/latest/minimal.html) [[本项目地址]](https://pypi.org/project/jiange/)

## 功能测试

### 本地开发测试

```bash
# 创建环境
mkvirtualenv jiange -p /usr/bin/python3
# 测试功能
xxx
```

### 本地打包测试

```bash
# 创建环境
mkvirtualenv test -p /usr/bin/python3
cd /Users/zhanglinjian1/Documents/project/jiange
workon test
# 安装本包（修改后也可实时生效）
pip install -e .
```

### 上传到pypi

```bash
# 注册 & 生成 source distribution
python setup.py register sdist
# 上传至 pypi
twine upload dist/*
```

## 版本管理

```bash
# 先在 setup.py & project/version.json 中设置新的版本
# 再运行下面命令
sh build.sh update first
```
