#!/usr/bin/python
# -*- coding: UTF-8 -*-
import hashlib
import os
import string
import oss2


# 阿里云bucket
from common.model.Response import Response
from config import settings
from utils.crypto.Md5Util import Md5Util

bucket = oss2.Bucket(oss2.Auth(settings.ALI_OSS_KEY, settings.ALI_OSS_SECRET),
                     settings.ALI_OSS_ENDPOINT, settings.ALI_OSS_BUCKET)


#
# 描述  阿里云OSS工具
# @author dejian.liu
# @date 2022-08-01 10:28
#
class OssUtil:
    # """
    #  从阿里云下载文件
    #  :param oss_key 待下载文件KEY
    #  :param file_dir 指定下载 文件路径，可以为空，为空的话默认下载到当前目录
    # """
    @staticmethod
    def download_file(oss_key, *file_dir):
        download_path = os.getcwd();
        if len(file_dir) > 0:
            download_path = file_dir[0]
            if not os.path.exists(download_path):
                os.makedirs(download_path)

        file_segs = oss_key.split("/");
        file_name = file_segs[len(file_segs) - 1]
        current_file = download_path + "/" + file_name
        result = bucket.get_object_to_file(oss_key, current_file)

        if 200 == result.status:
            return Response.success(current_file)
        else:
            return Response.fail(result.resp)

    # """
    # 删除文件
    # :param oss_key 待删除文件的KEY
    # """

    @staticmethod
    def remove_file(oss_key):
        result = bucket.delete_object(oss_key)
        if 200 == result.status:
            return Response.success()
        else:
            return Response.fail(result.resp)

    # """
    # 文件上传
    # :param file_path 待上传的文件
    # :param oss_key 用户自定义上传KEY
    # """
    @staticmethod
    def upload_file(file_path, oss_key=None):
        if not os.path.exists(file_path) or os.path.isdir(file_path):
            raise Exception("待上传文件:{} 不存在".format(file_path))

        if oss_key is None:
            oss_key = "common/" + Md5Util.get_md5_file(file_path)
        result = bucket.put_object_from_file(oss_key, file_path)

        if 200 == result.status:
            return Response.success(oss_key)
        else:
            return Response.fail(result.resp)
