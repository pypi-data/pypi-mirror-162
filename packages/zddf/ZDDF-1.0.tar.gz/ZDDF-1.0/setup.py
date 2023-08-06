from setuptools import setup, find_packages
from distutils.core import setup

setup(
    name = "ZDDF",   # 对外的模块名字
    version = "1.0",    # 版本号
    description = "自动打分",   # 信息描述
    author = "keyee",# 作者
    author_email = "du1872779171@163.com",
    py_modules=["ASS.ASS"] # 要发布的模块
)
