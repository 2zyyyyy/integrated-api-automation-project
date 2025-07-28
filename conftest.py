import pytest
import os
from utils.config_utils import load_env_config, load_db_config, load_redis_config, load_mq_config
from utils.db_utils import MySQLClient
from utils.redis_utils import RedisClient
from utils.mq_utils import RabbitMQClient
from utils.log_utils import logger, set_case_context, clear_case_context

# 自定义命令行参数
def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        default="test",
        help="指定测试环境：test（默认）/staging/prod"
    )

# 核心夹具
@pytest.fixture(scope="session")
def env_name(request):
    return request.config.getoption("--env")

@pytest.fixture(scope="session")
def env_config(env_name):
    config = load_env_config(env_name)
    logger.info(f"加载环境配置：{env_name}，基础URL：{config['base_url']}")
    return config

# 数据层客户端夹具
@pytest.fixture(scope="class")
def db_client(db_config):
    logger.info(f"初始化数据库连接：{db_config['host']}:{db_config['port']}")
    client = MySQLClient(config=db_config)
    yield client
    client.close()
    logger.info("关闭数据库连接")

# 用例级日志上下文管理
@pytest.fixture(autouse=True)
def case_log_context(request):
    """自动为每个用例设置日志上下文"""
    case_name = request.node.name
    case_id = set_case_context(case_name)
    logger.info(f"开始执行用例：{case_name}，用例ID：{case_id}")
    yield
    logger.info(f"用例执行结束：{case_name}，用例ID：{case_id}")
    clear_case_context()

# 用例结果记录钩子
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call":
        if rep.failed:
            logger.error(f"用例执行失败：{item.node.name}，原因：{str(rep.longrepr)}")
        elif rep.passed:
            logger.info(f"用例执行成功：{item.node.name}")
        else:
            logger.warning(f"用例执行跳过：{item.node.name}")