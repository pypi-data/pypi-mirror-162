#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述: 枚举集合
# @author: dejian.liu
# @date:  2022-08-02 11:56

from enum import Enum, unique


# 事件数据类型
class DataType(Enum):
    TEXT = 1
    JSON = 2


# 数据应用场景
class DataScene(Enum):
    WORD_COUNT = 1  # 单词统计
    CALC_SUMMARY = 2  # 计算摘要
