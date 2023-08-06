from setuptools import setup


requirements = '''
bleach==5.0.1
certifi==2022.6.15
charset-normalizer==2.1.0
commonmark==0.9.1
docutils==0.19
idna==3.3
importlib-metadata==4.12.0
keyring==23.7.0
pkginfo==1.8.3
pyahocorasick==1.4.4
Pygments==2.12.0
readme-renderer==36.0
requests==2.28.1
requests-toolbelt==0.9.1
rfc3986==2.0.0
rich==12.5.1
six==1.16.0
twine==4.0.1
typing_extensions==4.3.0
urllib3==1.26.11
webencodings==0.5.1
xlrd==2.0.1
XlsxWriter==3.0.3
zipp==3.8.1
'''
install_requires = [x.strip() for x in requirements.split('\n') if x.strip()]


setup(
    name='jiange',
    version='0.1.3',
    description='functions to save your life',
    url='http://github.com/linjianz',
    author='Zhang Linjian',
    author_email='zhanglinjian1@gmail.com',
    license='MIT',
    packages=['jiange'],
    install_requires=install_requires,
    zip_safe=False)
