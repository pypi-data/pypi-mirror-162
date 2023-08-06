#!/usr/bin/python
# -*- coding: UTF-8 -*-


#
# 描述  通用响应对象
# @author dejian.liu
# @date 2022-08-01 10:28
#
from ldj.common import Constant
from ldj.utils.json.JsonUtil import JsonUtil
from pydantic import BaseModel


class Response(BaseModel):
    """
    :param status 为http状态
    :param msg 响应消息
    :param code 业务编码
    :param data 业务数据
    """
    status: int = Constant.HTTP_SUCCESS
    message: str = ""
    code: int = Constant.BIZ_SUCCESS
    result: object = None

    def toJson(self):
        return JsonUtil.toJson(self)

    @staticmethod
    def success(status=None, message=None, code=None, result=None):
        if status is None:
            status = Constant.HTTP_SUCCESS
        if message is None:
            message = "ok"
        if code is None:
            code = Constant.BIZ_SUCCESS
        res = Response()
        res.status = status
        res.message = message
        res.code = code
        res.result = result
        return res

    @staticmethod
    def fail(status=None, message=None, code=None, result=None):
        res = Response()
        if status is None:
            status = Constant.HTTP_ERROR
        if message is None:
            message = "error"
        if code is None:
            code = Constant.BIZ_ERROR
        res.status = status
        res.message = message
        res.code = code
        res.result = result
        return res
