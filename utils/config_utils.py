import yaml
import os
from pathlib import Path
from utils.log_utils import logger

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

def _load_yaml_config(file_path):
    """加载YAML配置文件"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"配置文件不存在: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"配置文件解析错误: {file_path}, 错误: {str(e)}")
        raise

def load_env_config(env_name):
    """加载环境基础配置"""
    config_path = os.path.join(PROJECT_ROOT, "config", "env.yaml")
    all_config = _load_yaml_config(config_path)
    
    if env_name not in all_config:
        raise ValueError(f"环境配置不存在: {env_name}")
    
    config = all_config[env_name]
    config["env"] = env_name
    logger.info(f"加载环境配置: {env_name}")
    return config

def load_db_config(env_name):
    """加载数据库配置"""
    config_path = os.path.join(PROJECT_ROOT, "config", "db_config.yaml")
    all_config = _load_yaml_config(config_path)
    
    if env_name not in all_config:
        raise ValueError(f"数据库配置不存在: {env_name}")
    
    logger.info(f"加载数据库配置: {env_name}")
    return all_config[env_name]

def load_redis_config(env_name):
    """加载Redis配置"""
    config_path = os.path.join(PROJECT_ROOT, "config", "redis_config.yaml")
    all_config = _load_yaml_config(config_path)
    
    if env_name not in all_config:
        raise ValueError(f"Redis配置不存在: {env_name}")
    
    logger.info(f"加载Redis配置: {env_name}")
    return all_config[env_name]

def load_mq_config(env_name):
    """加载MQ配置"""
    config_path = os.path.join(PROJECT_ROOT, "config", "mq_config.yaml")
    all_config = _load_yaml_config(config_path)
    
    if env_name not in all_config:
        raise ValueError(f"MQ配置不存在: {env_name}")
    
    logger.info(f"加载MQ配置: {env_name}")
    return all_config[env_name]

def load_schema(schema_name):
    """加载JSON Schema验证文件"""
    schema_path = os.path.join(PROJECT_ROOT, "config", "schemas", f"{schema_name}.json")
    logger.info(f"加载Schema验证: {schema_name}")
    return _load_yaml_config(schema_path)
