#!/usr/bin/env python
# coding: utf-8
from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fd:
    long_description = fd.read()

setup(
    name = 'ChatRoom-jianjun',
    version = '2.1.2',
    author = 'jianjun',
    author_email = '910667956@qq.com',
    url = 'https://github.com/EVA-JianJun/ChatRoom',
    description = u'Python分布式交互框架！快速建立可靠的网络连接！',
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = ["ChatRoom"],
    install_requires = [
        "rsa>=4.0",
        "bcrypt>=3.2.0",
        "psutil>=5.7.0",
        "tqdm>=4.44.1",
        "Mconfig>=1.1.4",
        "ttkbootstrap>=1.9.0",
        "yagmail>=0.15.280"
    ],
    entry_points={
        'console_scripts': [
            'room=ChatRoom:_RunRoom'
        ],
    },
    package_data={
    '': ['config/*', '.Room/audio/*', '.Room/image/*'],
    },
)