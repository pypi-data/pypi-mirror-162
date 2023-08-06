#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述: AOP 面向切面编程
# @author: dejian.liu
# @date:  2022-08-05 13:50

from functools import wraps

'''
aop对象
'''


class Aop(object):
    # 构造方法
    def __init__(self, before=None,
                 after=None,
                 exception=None,
                 final=None):
        self.before = before
        self.after = after
        self.exception = exception
        self.final = final

    # 调用函数时触发
    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            func_result = None
            # 拦截执行的中间结果
            middle_kwargs = kwargs.copy()
            if self.before is not None:
                result = self.before(*args, **kwargs)
                if result is not None:
                    middle_kwargs["before_result"] = result
            try:
                func_result = func(*args, **kwargs)
                if self.after is not None:
                    result = self.after(*args, **middle_kwargs)
                    if result is not None:
                        middle_kwargs["after_result"] = result
            except Exception as e:
                if self.exception is not None:
                    result = self.exception(*args, **middle_kwargs)
                    if result is not None:
                        middle_kwargs["exception_result"] = result
                print(e)
            finally:
                if self.final is not None:
                    result = self.final(*args, **middle_kwargs)
                    if result is not None:
                        middle_kwargs["final_result"] = result
            return func_result

        return wrapper
