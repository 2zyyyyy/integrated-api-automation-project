import pymysql
from pymysql.cursors import DictCursor
from contextlib import contextmanager
import os
from dotenv import load_dotenv
from utils.log_utils import logger

load_dotenv()

class MySQLClient:
    def __init__(self, config):
        self.config = config
        self.connection = None

    def connect(self):
        """建立数据库连接"""
        if self.connection and self.connection.open:
            return self.connection

        try:
            self.connection = pymysql.connect(
                host=self.config["host"],
                port=self.config["port"],
                user=self.config["user"],
                password=os.getenv(self.config["password_key"]),
                database=self.config["database"],
                charset=self.config.get("charset", "utf8mb4"),
                cursorclass=DictCursor
            )
            logger.info(f"数据库连接成功: {self.config['host']}:{self.config['port']}/{self.config['database']}")
            return self.connection
        except Exception as e:
            logger.error(f"数据库连接失败: {str(e)}")
            raise

    @contextmanager
    def get_cursor(self, commit=False):
        """数据库游标上下文管理器"""
        self.connect()
        cursor = self.connection.cursor()
        
        try:
            yield cursor
            if commit:
                self.connection.commit()
                logger.debug("数据库事务已提交")
        except Exception as e:
            self.connection.rollback()
            logger.error(f"数据库操作失败，已回滚: {str(e)}")
            raise
        finally:
            cursor.close()

    def execute_sql(self, sql, params=None, commit=False):
        """执行SQL语句"""
        logger.debug(f"执行SQL: {sql}, 参数: {params}")
        
        with self.get_cursor(commit=commit) as cursor:
            cursor.execute(sql, params or ())
            
            # 查询语句返回结果
            if sql.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()
                logger.debug(f"查询结果: {len(result)} 条记录")
                return result
            
            # 非查询语句返回影响行数
            logger.debug(f"影响行数: {cursor.rowcount}")
            return cursor.rowcount

    def close(self):
        """关闭数据库连接"""
        if self.connection and self.connection.open:
            self.connection.close()
            logger.info("数据库连接已关闭")

def get_db_client(env="test"):
    """快捷获取数据库客户端"""
    from utils.config_utils import load_db_config
    return MySQLClient(load_db_config(env))
