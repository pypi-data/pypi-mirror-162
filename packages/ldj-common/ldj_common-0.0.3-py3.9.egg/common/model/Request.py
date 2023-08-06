#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述: 请求对象
# @author: dejian.liu
# @date:  2022-08-10 15:19
from pydantic import BaseModel


class Request(BaseModel):
    body: object = None
    start: int = 0
    limit: int = 10
    params: dict = None

    @staticmethod
    def build(body: object, start: int, limit: int):
        req = Request()
        req.body = body
        req.start = start
        req.limit = limit
        return req
