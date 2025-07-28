# integrated-api-automation-project

# 接口自动化测试框架

基于 Python+requests+pytest+allure 的接口自动化测试框架，集成数据库、缓存、消息队列操作及接口加解密能力，支持多环境切换和全面的测试报告生成。


## 框架特点

- **多环境支持**：通过命令行参数快速切换测试/预生产环境
- **完整数据层集成**：MySQL、Redis、RabbitMQ 操作封装
- **接口安全保障**：支持 AES/RSA 加解密及签名验证
- **全方位日志系统**：结构化日志记录，含用例执行、接口请求、错误详情
- **灵活的测试数据管理**：测试数据与用例分离，支持数据驱动
- **丰富的报告能力**：生成 Allure 可视化报告，含趋势分析和失败详情
- **高可扩展性**：模块化设计，新增业务模块只需按规范添加文件


## 目录结构

```
api_auto_test/
├── .env.example               # 环境变量模板（敏感信息）
├── .gitignore                 # Git忽略文件配置
├── pytest.ini                 # pytest全局配置
├── conftest.py                # pytest夹具和钩子函数
├── requirements.txt           # 项目依赖清单
├── README.md                  # 框架说明文档
│
├── config/                    # 配置文件目录
│   ├── env.yaml               # 多环境基础配置（URL、超时等）
│   ├── db_config.yaml         # 数据库连接配置
│   ├── redis_config.yaml      # Redis连接配置
│   ├── mq_config.yaml         # 消息队列配置
│   └── schemas/               # JSON Schema验证文件
│
├── api/                       # 接口封装层
│   ├── base_api.py            # 基础接口类（通用请求逻辑）
│   ├── user_api.py            # 用户模块接口
│   └── order_api.py           # 订单模块接口
│
├── cases/                     # 测试用例层
│   ├── test_user.py           # 用户模块测试用例
│   └── test_order.py          # 订单模块测试用例
│
├── data/                      # 测试数据层
│   ├── user_data.yaml         # 用户模块测试数据
│   └── order_data.yaml        # 订单模块测试数据
│
├── utils/                     # 工具函数层
│   ├── config_utils.py        # 配置加载工具
│   ├── db_utils.py            # MySQL操作工具
│   ├── redis_utils.py         # Redis操作工具
│   ├── mq_utils.py            # 消息队列操作工具
│   ├── crypto_utils.py        # 加解密工具
│   ├── assert_utils.py        # 断言工具
│   └── log_utils.py           # 日志工具
│
└── reports/                   # 报告输出目录
    ├── allure_results/        # Allure报告原始数据
    ├── allure_report/         # 生成的HTML报告
    └── logs/                  # 日志文件
        ├── test_20231026.log  # 日常日志（按日期）
        └── error_20231026.log # 错误日志（按日期）
```


## 快速开始

### 1. 环境准备

- Python 3.8+
- 安装依赖：
  ```bash
  pip install -r requirements.txt
  ```
- 安装 Allure 报告工具（用于生成可视化报告）：
  - Windows：从 [Allure 官网](https://github.com/allure-framework/allure2/releases) 下载并配置环境变量
  - macOS：`brew install allure`


### 2. 配置环境

1. 复制环境变量模板并填写实际值：
   ```bash
   cp .env.example .env
   ```
   需配置的核心信息：
   - 数据库密码（`DB_TEST_PASSWORD`）
   - Redis 密码（`REDIS_TEST_PASSWORD`）
   - 加解密密钥（`AES_SECRET_KEY`、`RSA_PUBLIC_KEY`等）

2. 根据实际环境修改 `config/` 目录下的配置文件：
   - `env.yaml`：配置接口基础 URL、超时时间等
   - `db_config.yaml`：配置数据库地址、端口、用户名等


### 3. 执行测试

#### 基本执行
```bash
# 执行所有用例（默认测试环境）
pytest
```

#### 指定环境
```bash
# 执行预生产环境用例
pytest --env staging
```

#### 生成 Allure 报告
```bash
# 执行用例并生成报告数据
pytest --alluredir=reports/allure_results

# 从数据生成HTML报告
allure generate reports/allure_results -o reports/allure_report --clean

# 打开报告（自动启动浏览器）
allure open reports/allure_report
```

#### 高级用法
```bash
# 并行执行（根据CPU核心数自动分配）
pytest -n auto

# 只执行标记为"smoke"的冒烟用例
pytest -m smoke

# 失败重跑2次，每次间隔1秒
pytest --reruns 2 --reruns-delay 1

# 显示详细日志（调试用）
pytest -s -v
```


## 测试用例编写规范

1. **用例组织**：
   - 按业务模块创建测试文件（如 `test_user.py`）
   - 类名以 `Test` 开头（如 `TestUserAPI`）
   - 用例方法以 `test_` 开头（如 `test_login_success`）

2. **用例内容**：
   - 使用 Allure 注解分类（`@allure.feature`/`@allure.story`）
   - 前置条件在 `setup_class` 中实现（如初始化接口对象、准备测试数据）
   - 后置条件在 `teardown_class` 中实现（如清理测试数据）
   - 断言优先使用 `utils/assert_utils.py` 中的封装方法

3. **示例用例**：
```python
import allure
from api.user_api import UserAPI
from utils.assert_utils import assert_response_success

@allure.feature("用户模块")
class TestUserAPI:
    def setup_class(self):
        self.user_api = UserAPI()  # 初始化接口对象

    @allure.story("用户登录")
    @allure.title("使用正确账号密码登录")
    def test_login_success(self):
        # 执行登录请求
        response = self.user_api.login("test_user", "test_password")
        
        # 验证响应
        assert_response_success(response)
        assert "token" in response["data"], "登录响应中未包含token"
```


## 日志说明

1. **日志级别**：
   - `DEBUG`：详细调试信息（如接口请求参数、响应数据）
   - `INFO`：正常执行信息（如用例开始、结束）
   - `WARNING`：警告信息（如接口响应时间过长）
   - `ERROR`：错误信息（如接口调用失败、断言失败）
   - `CRITICAL`：严重错误（如数据库连接失败）

2. **日志查看**：
   - 控制台输出 `INFO` 及以上级别日志
   - 详细日志存储在 `reports/logs/` 目录（按日期命名）
   - 错误日志单独存储在 `reports/logs/error_*.log` 中

3. **敏感数据处理**：
   - 密码、token等敏感信息会自动脱敏（替换为 `***`）
   - 如需调整脱敏规则，修改 `utils/log_utils.py` 中的 `mask_sensitive_data` 函数


## 扩展指南

1. **新增业务接口**：
   - 在 `api/` 目录下创建接口文件（如 `product_api.py`）
   - 接口类继承 `BaseAPI`
   - 实现具体接口方法（如 `get_product_detail`）

2. **新增测试用例**：
   - 在 `cases/` 目录下创建测试文件（如 `test_product.py`）
   - 按规范编写测试类和用例方法

3. **添加新工具**：
   - 在 `utils/` 目录下创建工具文件（如 `excel_utils.py`）
   - 实现工具类和方法，在其他模块中导入使用


## 注意事项

1. **敏感信息安全**：
   - `.env` 文件包含敏感信息，已通过 `.gitignore` 排除，请勿提交到代码仓库
   - 日志中自动脱敏敏感信息，但仍需避免在代码中明文硬编码敏感数据

2. **环境清理**：
   - 测试数据应使用专门的测试账号和测试数据，避免影响生产数据
   - 确保 `teardown_class` 中包含数据清理逻辑，避免测试残留数据干扰

3. **版本兼容性**：
   - 依赖版本已在 `requirements.txt` 中固定，如需升级请先测试兼容性
   - 工具类版本需与接口服务版本匹配（如加解密算法需与后端一致）
