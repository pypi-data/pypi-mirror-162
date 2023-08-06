import json
from toolbox import ObjectDict


#
# 描述  JSON工具类
# @author dejian.liu
# @date 2022-08-01 10:28
#
class JsonUtil:

    @staticmethod
    def format(self):
        d = {}
        d.update(self.__dict__)
        return d

    @staticmethod
    def toJson(obj):
        return json.dumps(obj, skipkeys=True, ensure_ascii=False, default=JsonUtil.format)

    @staticmethod
    def toObject(json_str):
        json_obj = json.loads(json_str)
        if type(json_obj).__name__ == 'dict':
            return ObjectDict(json_obj)
        return json_obj
