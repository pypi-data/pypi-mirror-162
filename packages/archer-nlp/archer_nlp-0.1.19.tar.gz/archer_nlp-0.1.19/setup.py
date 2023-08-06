# coding:utf8

from setuptools import setup, find_packages

setup(
    name='archer_nlp',
    version='0.1.19',
    description='archer nlp',
    long_description='',
    license='',
    url='https://github.com/beybin/archer_nlp',
    author='beybin',
    author_email='1092386160@qq.com',
    install_requires=["pandas", "numpy", "python-Levenshtein", "pymongo", "pymysql", "sqlalchemy"],
    packages=find_packages()
)
