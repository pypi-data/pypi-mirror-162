#!/usr/bin/python
# -*- coding: UTF-8 -*-

#
# 描述  MD5加密工具
# @author dejian.liu
# @date 2022-08-01 10:28
#
import hashlib
import os.path


class Md5Util:
    """
    MD5加密文本
    :param word 待加密字符串
    """

    @staticmethod
    def get_md5(word):
        if isinstance(word, str):
            word = word.encode("utf-8")
        else:
            raise Exception("待加密参数必须为字符串")
        m = hashlib.md5()
        m.update(word)
        return m.hexdigest()

    """
    获取文件MD5
    :param file_path 待加密文件
    """

    @staticmethod
    def get_md5_file(file_path):
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            raise Exception("文件{}不存在".format(file_path))
        with open(file_path, 'rb') as f:
            md5obj = hashlib.md5()
            md5obj.update(f.read())
            return md5obj.hexdigest()
