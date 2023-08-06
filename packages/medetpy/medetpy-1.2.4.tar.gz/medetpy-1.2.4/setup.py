'''
Author: your name
Date: 2022-08-05 16:15:22
LastEditTime: 2022-08-06 15:38:36
LastEditors: your name
Description: 
FilePath: \medetpy\setup.py
'''
import setuptools #导入setuptools打包工具
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
 
setuptools.setup(
    name="medetpy", # 用自己的名替换其中的YOUR_USERNAME_
    version="1.2.4",    #包版本号，便于维护版本
    author="Grant-M",    #作者，可以写自己的姓名
    author_email="Grant_M@gmail.com",    #作者联系方式，可写自己的邮箱地址
    description="med-met",#包的简述
    long_description=long_description,    #包的详细介绍，一般在README.md文件内
    long_description_content_type="text/markdown",
    url="https://github.com/MG/med-met",    #自己项目地址，比如github的项目地址
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['requests','medpy'],
    python_requires='>=3.6',    #对python的最低版本要求
)