#!/usr/bin/python
# -*- coding: UTF-8 -*-


#
# 描述  通用响应对象
# @author dejian.liu
# @date 2022-08-01 10:28
#
from common import Constant
from utils.json.JsonUtil import JsonUtil
from pydantic import BaseModel


class Response(BaseModel):
    status: int = Constant.HTTP_SUCCESS
    message: str = None
    code: int = Constant.BIZ_SUCCESS
    result: object = None
    """
    :param status 为http状态
    :param msg 响应消息
    :param code 业务编码
    :param data 业务数据
    """

    def __init__(self, status, message):
        self.status = status
        self.message = message
        self.code = None
        self.result = None

    def set_result(self, result):
        self.result = result
        return self

    def set_code(self, code):
        self.code = code
        return self

    def set_status(self, status):
        self.status = status
        return self

    def set_msg(self, msg):
        self.msg = msg
        return self

    def toJson(self):
        return JsonUtil.toJson(self)

    @staticmethod
    def successOk():
        return Response.success(Constant.HTTP_SUCCESS, "ok")

    @staticmethod
    def successData(data):
        return Response.success(Constant.HTTP_SUCCESS, "ok", data)

    @staticmethod
    def success(status, msg, data=None):
        res = Response(status, msg)
        res.set_result(data)
        return res

    @staticmethod
    def fail(status, msg, code=None):
        res = Response(status, msg)
        res.set_code(code)
        return res

    @staticmethod
    def failMsg(msg):
        return Response.fail(Constant.HTTP_ERROR, msg)
