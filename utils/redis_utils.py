import redis
import os
from dotenv import load_dotenv
from utils.log_utils import logger

load_dotenv()

class RedisClient:
    def __init__(self, config):
        self.config = config
        self.client = None

    def connect(self):
        """建立Redis连接"""
        if self.client:
            try:
                self.client.ping()
                return self.client
            except Exception:
                logger.warning("Redis连接已断开，尝试重新连接")

        try:
            self.client = redis.Redis(
                host=self.config["host"],
                port=self.config["port"],
                password=os.getenv(self.config["password_key"]),
                db=self.config["db"],
                decode_responses=self.config.get("decode_responses", True),
                socket_connect_timeout=5
            )
            self.client.ping()
            logger.info(f"Redis连接成功: {self.config['host']}:{self.config['port']}/db{self.config['db']}")
            return self.client
        except Exception as e:
            logger.error(f"Redis连接失败: {str(e)}")
            raise

    def get(self, key):
        """获取键值"""
        self.connect()
        value = self.client.get(key)
        logger.debug(f"Redis获取: {key} -> {value}")
        return value

    def set(self, key, value, expire=None):
        """设置键值"""
        self.connect()
        result = self.client.set(key, value, ex=expire)
        logger.debug(f"Redis设置: {key} = {value}, 过期时间: {expire}")
        return result

    def delete(self, key):
        """删除键"""
        self.connect()
        result = self.client.delete(key)
        logger.debug(f"Redis删除: {key} -> {'成功' if result else '失败'}")
        return result

    def keys(self, pattern="*"):
        """查找匹配的键"""
        self.connect()
        return self.client.keys(pattern)

    def flush_db(self):
        """清空当前数据库"""
        self.connect()
        logger.warning("清空Redis当前数据库")
        return self.client.flushdb()

    def close(self):
        """关闭连接"""
        if self.client:
            self.client.close()
            logger.info("Redis连接已关闭")

def get_redis_client(env="test"):
    """快捷获取Redis客户端"""
    from utils.config_utils import load_redis_config
    return RedisClient(load_redis_config(env))
