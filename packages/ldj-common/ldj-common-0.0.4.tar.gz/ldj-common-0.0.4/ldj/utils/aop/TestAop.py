#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述:
# @author: dejian.liu
# @date:  2022-08-05 14:31
from functools import wraps


class D(object):
    def __init__(self, before=None, after=None):
        self.before = before
        self.after = after

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            middle_result = kwargs.copy()
            beforeResult = self.before(args, middle_result)
            print(beforeResult)
            middle_result["name1"] = "liudejian"
            result = func(*args, **kwargs)
            if self.after is not None:
                self.after(*args, **middle_result)
            print("在函数执行后，做一些操作")
            return result

        return wrapper


def beforeF(*args, **kwargs):
    print("========before======={},{}".format(args, kwargs))
    return "liudejian"


def afterF(*args, **kwargs):
    print(kwargs)
    print("=====after====={}={}".format(args,kwargs))
    return "after111"


@D(before=beforeF, after=afterF)
def query(name, age):
    print('函数执行中。。。')
    return "我是 {}, 今年{}岁 ".format(name, age)


print(query('Amos', 24))
