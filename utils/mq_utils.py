import pika
import os
import json
from threading import Thread
import time
from dotenv import load_dotenv
from utils.log_utils import logger

load_dotenv()

class RabbitMQClient:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.channel = None
        self.consume_threads = []

    def connect(self):
        """建立MQ连接"""
        if self.connection and self.connection.is_open:
            return self.channel

        try:
            credentials = pika.PlainCredentials(
                self.config["user"],
                os.getenv(self.config["password_key"])
            )
            
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.config["host"],
                    port=self.config["port"],
                    credentials=credentials,
                    virtual_host=self.config.get("virtual_host", "/"),
                    heartbeat=600
                )
            )
            
            self.channel = self.connection.channel()
            logger.info(f"MQ连接成功: {self.config['host']}:{self.config['port']}")
            return self.channel
        except Exception as e:
            logger.error(f"MQ连接失败: {str(e)}")
            raise

    def declare_queue(self, queue_name, durable=False, exclusive=False, auto_delete=False):
        """声明队列"""
        self.connect()
        self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete
        )
        logger.info(f"MQ队列已声明: {queue_name}")

    def publish_message(self, queue_name, message, exchange='', routing_key=None):
        """发送消息"""
        self.connect()
        routing_key = routing_key or queue_name
        
        # 序列化消息
        if isinstance(message, dict):
            message = json.dumps(message)
        elif not isinstance(message, str):
            message = str(message)

        self.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # 消息持久化
                content_type='application/json' if isinstance(message, dict) else 'text/plain'
            )
        )
        logger.info(f"MQ消息已发送: 队列={queue_name}, 内容={message[:100]}...")

    def consume_messages(self, queue_name, callback, auto_ack=True, max_messages=None):
        """消费消息"""
        self.connect()
        self.declare_queue(queue_name)
        
        messages_received = 0
        
        def on_message(ch, method, properties, body):
            nonlocal messages_received
            try:
                # 解析消息
                try:
                    data = json.loads(body)
                except:
                    data = body.decode('utf-8') if isinstance(body, bytes) else body
                
                # 调用回调函数
                callback(data)
                messages_received += 1
                
                # 达到最大消息数则停止消费
                if max_messages and messages_received >= max_messages:
                    ch.stop_consuming()
                    
            except Exception as e:
                logger.error(f"MQ消息处理失败: {str(e)}")
                
            if not auto_ack:
                ch.basic_ack(delivery_tag=method.delivery_tag)

        # 启动消费线程
        def consume():
            self.channel.basic_consume(
                queue=queue_name,
                on_message_callback=on_message,
                auto_ack=auto_ack
            )
            logger.info(f"开始消费MQ消息: {queue_name}")
            self.channel.start_consuming()

        thread = Thread(target=consume, daemon=True)
        thread.start()
        self.consume_threads.append(thread)
        return thread

    def close(self):
        """关闭连接"""
        # 停止所有消费线程
        for thread in self.consume_threads:
            if thread.is_alive():
                if self.channel:
                    self.channel.stop_consuming()
                thread.join(timeout=5)
        
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("MQ连接已关闭")

def get_mq_client(env="test"):
    """快捷获取MQ客户端"""
    from utils.config_utils import load_mq_config
    return RabbitMQClient(load_mq_config(env))
