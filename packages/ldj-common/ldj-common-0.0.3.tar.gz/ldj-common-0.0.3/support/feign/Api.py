#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述:
# @author: dejian.liu
# @date:  2022-08-04 12:34
class Api:
    def __init__(self, uri, name=None, serverUrl=None, desc=None):
        self.uri = uri
        self.name = name
        self.serverUrl = serverUrl
        self.desc = desc