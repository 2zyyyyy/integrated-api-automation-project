import allure
import pytest
import json
from api.user_api import UserAPI
from utils.assert_utils import assert_response_success, assert_schema_match
from utils.log_utils import logger
from data.user_data import login_success_cases, login_fail_cases

@allure.feature("用户模块")
class TestUserAPI:
    def setup_class(self):
        self.user_api = UserAPI(self.env_config)
        self.token = None  # 存储登录token

    @allure.story("用户登录")
    @allure.title("正常登录流程")
    @pytest.mark.smoke
    def test_login_success(self):
        # 从测试数据获取参数
        case_data = login_success_cases[0]
        logger.info(f"使用测试数据：{json.dumps(case_data, ensure_ascii=False)}")
        
        # 执行登录
        response = self.user_api.login(
            username=case_data["username"],
            password=case_data["password"]
        )
        
        # 验证响应
        assert_response_success(response)
        assert "token" in response["data"], "响应中未包含token"
        
        # 验证响应结构
        assert_schema_match(response, "user_schema")
        
        # 保存token供后续用例使用
        self.token = response["data"]["token"]
        logger.info("登录成功，获取到token")

    @allure.story("用户登录")
    @allure.title("登录失败场景：{case_data['description']}")
    @pytest.mark.parametrize("case_data", login_fail_cases)
    def test_login_failure(self, case_data):
        logger.info(f"测试场景：{case_data['description']}，参数：{case_data['username']}/{case_data['password']}")
        
        # 执行登录
        response = self.user_api.login(
            username=case_data["username"],
            password=case_data["password"]
        )
        
        # 验证失败响应
        assert response["code"] == case_data["expected_code"], \
            f"预期状态码{case_data['expected_code']}，实际{response['code']}"
        assert case_data["expected_msg"] in response["message"], \
            f"预期消息包含{case_data['expected_msg']}，实际{response['message']}"

    @allure.story("用户信息")
    @allure.title("获取当前用户信息")
    def test_get_current_user_info(self):
        # 前置条件检查
        assert self.token is not None, "请先执行登录用例获取token"
        logger.info("开始获取用户信息，使用已保存的token")
        
        # 执行接口
        response = self.user_api.get_current_user(self.token)
        
        # 验证响应
        assert_response_success(response)
        assert "username" in response["data"], "用户信息中缺少用户名"
        logger.info(f"获取用户信息成功：{response['data']['username']}")