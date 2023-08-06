#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述:
# @author: dejian.liu
# @date:  2022-08-10 14:02
from setuptools import setup, find_packages

setup(
    name="ldj-common",
    version="0.0.5",
    author="ldj",
    author_email="zuiwoxing@qq.com",
    description="LDJ公共库(aop/crypto/json/nacos/oss/kafka)",
    long_description_content_type="text/markdown",
    url="https://www.messagesea.com/",
    packages= find_packages(),
    classifiers=[
        # 发展时期,常见的如下
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        # 开发的目标用户
        'Intended Audience :: Developers',
        # 属于什么类型
        'Topic :: Software Development :: Build Tools',
        # 许可证信息
        'License :: OSI Approved :: MIT License',
        # 目标 Python 版本
        'Programming Language :: Python :: 3.8',
    ],
)
