#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述: feign 客户端
# @author: dejian.liu
# @date:  2022-08-04 9:55
import os
import sys

from support.feign.Api import Api

apis = dict()


# '''
# @FeignClient 注解
# '''
def FeignClient(meta: Api):
    def decorator(func):
        func.__annotations__["meta"] = meta
        return func

    return decorator


# '''
# 注册restAPI接口
# '''
def register(func):
    if func is None:
        return
    meta_api: Api = func.__annotations__.get("meta")
    if meta_api is None:
        return
    apis[meta_api.uri] = meta_api


@FeignClient(meta=Api(uri="api/nlp/summary", name="计算摘要", serverUrl="http://127.0.0.1:8000"))
def summary(param):
    print("test===" + param)
    return param + " good"


def parse_anno(fun):
    meta: Api = fun.__annotations__.get("meta")
    if meta is None:
        print("========meta is null=============")
    else:
        print(meta.uri)


import importlib

if __name__ == "__main__":
    # summary("vaudevillian")
    # module = sys.modules[__name__]
    # sum = getattr(module, 'summary')
    # print(sum)
    # parse_anno(sum)
    modules = sys.modules
    print("===========================")
    for mod in modules:
        print(mod)
    print("----------------------")
    print(sys.modules["Api"])
