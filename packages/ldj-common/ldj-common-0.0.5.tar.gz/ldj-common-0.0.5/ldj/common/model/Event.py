#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述:
# @author: dejian.liu
# @date:  2022-08-02 10:26
from pydantic import BaseModel


class Event(BaseModel):
    dataType: int = None
    dataSence: int = None
    content: str = None

    # '''
    # :param dataType 1=text  2= json
    # :param dataSence 1=word_count
    # :param content 事件内容
    # '''
    def __init__(self, dataType, dataSence, content):
        self.dataType = dataType
        self.dataSence = dataSence
        self.content = content

    @staticmethod
    def build(dataType, dataSence, content):
        return Event(dataType, dataSence, content)
