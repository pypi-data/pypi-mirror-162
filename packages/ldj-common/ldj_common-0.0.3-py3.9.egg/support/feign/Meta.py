#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述:
# @author: dejian.liu
# @date:  2022-08-04 10:14

class ClassMeta:
    '''
    :param uri 请求接口的相对路径[必填]
    :param name 服务名称[可选]
    :param serverUrl 服务基础地址 (example:http(s)://localhost:8080)[可选]
    :param desc 服务描述[可选]
    '''
    def __init__(self, uri, name=None, serverUrl=None, desc=None):
        self.uri = uri
        self.name = name
        self.serverUrl = serverUrl
        self.desc = desc
