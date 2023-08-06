from setuptools import setup
from jiange.file import load_line


install_requires = load_line('requirements.txt')


setup(name='jiange',
      version='0.1.1',
      description='functions to save your life',
      url='http://github.com/linjian',
      author='Zhang Linjian',
      author_email='zhanglinjian1@gmail.com',
      license='MIT',
      packages=['jiange'],
      install_requires=install_requires,
      zip_safe=False)
