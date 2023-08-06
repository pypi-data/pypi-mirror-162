#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述:
# @author: dejian.liu
# @date:  2022-08-08 10:57
import threading


class ThreadLocal:
    box = {}

    def __setattr__(self, key, value):
        thread_id = threading.get_ident()
        # 单元格已存在
        if thread_id in ThreadLocal.box:
            ThreadLocal.box[thread_id][key] = value
        else:
            ThreadLocal.box[thread_id] = {key: value}

    def __getattr__(self, item):
        thread_id = threading.get_ident()
        return ThreadLocal.box[thread_id][item]

    def remove(self):
        thread_id = threading.get_ident()
        del ThreadLocal.box[thread_id]

