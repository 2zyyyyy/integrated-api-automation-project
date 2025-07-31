from api.base_api import BaseAPI
from utils.log_utils import logger

class UserAPI(BaseAPI):
    def __init__(self, env_config):
        super().__init__(env_config)
        self.base_path = "/api/v1/user"

    def login(self, username, password):
        """用户登录接口"""
        url = f"{self.base_path}/login"
        data = {
            "username": username,
            "password": password
        }
        logger.info(f"执行登录: username={username}")
        return self.post(url, json=data)

    def get_user_info(self, user_id, token):
        """获取用户信息接口"""
        url = f"{self.base_path}/{user_id}"
        headers = {"Authorization": f"Bearer {token}"}
        logger.info(f"获取用户信息: user_id={user_id}")
        return self.get(url, headers=headers)

    def register(self, user_data):
        """用户注册接口"""
        url = f"{self.base_path}/register"
        logger.info(f"执行用户注册: {user_data['username']}")
        return self.post(url, json=user_data)
