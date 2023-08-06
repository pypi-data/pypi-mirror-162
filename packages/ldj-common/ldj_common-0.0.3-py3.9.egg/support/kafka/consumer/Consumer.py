#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述: 消息消费者
# @author: dejian.liu
# @date:  2022-08-01 17:52
import json


from kafka3 import KafkaConsumer


class MessageConsumer:

    def __init__(self, brokers, topic_name, group_id):
        self.consumer = None
        self.brokers = brokers
        self.topic_name = topic_name
        self.group_id = group_id

    # 获取销毁者
    def get_consumer(self):
        return self.consumer

    # 启动consumer
    def start(self, callback):
        try:
            consumer = KafkaConsumer(self.topic_name,
                                     value_deserializer=json.loads,
                                     group_id=self.group_id,
                                     bootstrap_servers=[self.brokers])
            self.consumer = consumer
            for message in consumer:
                callback(message)
        except KeyboardInterrupt as e:
            print(e)

    # 关闭consumer
    def close(self):
        self.consumer.close(True)

    # 暂停
    def paused(self, *partitions):
        self.consumer.paused(partitions)

    # 恢复
    def resume(self, *partitions):
        self.consumer.resume(partitions)
