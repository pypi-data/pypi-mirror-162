#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 描述: 消息生产者
# @author: dejian.liu
# @date:  2022-08-01 21:41
import json

from kafka3 import KafkaProducer
from kafka3.errors import KafkaError

from utils.json.JsonUtil import JsonUtil


class MessageProducer:

    # '''
    # :param broker_servers kafka服务地址
    # :param topic_name 队列名称
    # :param key 消息发送的KEY,消息paration 路由使用
    # '''
    def __init__(self, broker_servers, topic_name, key=None):
        self.broker_servers = broker_servers
        self.topic_name = topic_name
        self.key = key
        self.producer = None
        self.producer = KafkaProducer(bootstrap_servers=broker_servers)

    # '''
    # 关闭producer
    # '''
    def close(self):
        try:
            self.producer.close()
        except KafkaError as e:
            print(e)

    # '''
    # 发送消息
    # :param data 待发送的消息体
    # '''
    def sendMessage(self, data):
        try:
            send_message = json.dumps(data, ensure_ascii=True, default=JsonUtil.format)
            producer = self.producer
            v = send_message.encode('utf-8')
            if self.key is None:
                self.key = "1"
            k = self.key.encode('utf-8')
            # print("send msg:(k,v)", k, v)
            future = producer.send(self.topic_name, key=k, value=v)
            producer.flush()
            return future
        except KafkaError as e:
            print(e)
