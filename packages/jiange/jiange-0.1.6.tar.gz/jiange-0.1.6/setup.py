from setuptools import setup


VERSION = 'v0.1.6'

requirements = '''
certifi==2022.6.15
charset-normalizer==2.1.0
idna==3.3
pyahocorasick==1.4.4
requests==2.28.1
tqdm==4.64.0
urllib3==1.26.11
xlrd==1.2.0
XlsxWriter==3.0.3
'''
install_requires = [x.strip() for x in requirements.split('\n') if x.strip()]

setup(
    name='jiange',
    version=VERSION[1:],
    description='functions to save your life',
    url='http://github.com/linjianz',
    author='Zhang Linjian',
    author_email='zhanglinjian1@gmail.com',
    license='MIT',
    packages=['jiange'],
    install_requires=install_requires,
    zip_safe=False)
