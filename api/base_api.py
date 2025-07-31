import requests
import json
from utils.crypto_utils import CryptoUtils
from utils.log_utils import logger

class BaseAPI:
    def __init__(self, env_config):
        self.base_url = env_config["base_url"]
        self.timeout = env_config.get("timeout", 10)
        self.headers = env_config.get("headers", {})
        self.encrypt_enabled = env_config.get("encrypt_enabled", False)
        self.crypto = CryptoUtils()
        self.session = requests.Session()  # 保持会话

    def _log_request(self, method, url, params=None, data=None, json=None, headers=None):
        """记录请求信息"""
        log_data = {
            "method": method,
            "url": url,
            "params": params,
            "headers": headers or self.headers
        }
        
        # 处理敏感数据脱敏
        if json:
            log_json = json.copy()
            if "password" in log_json:
                log_json["password"] = "***"
            log_data["json"] = log_json
        elif data:
            log_data["data"] = data
        
        logger.debug(f"发送请求：{json.dumps(log_data, ensure_ascii=False)}")

    def _log_response(self, response):
        """记录响应信息"""
        try:
            response_data = response.json()
            log_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "response_time": f"{response.elapsed.total_seconds():.3f}s",
                "data": response_data
            }
            logger.debug(f"收到响应：{json.dumps(log_data, ensure_ascii=False)}")
        except:
            logger.debug(
                f"收到响应：状态码={response.status_code}, "
                f"响应时间={response.elapsed.total_seconds():.3f}s, "
                f"内容={response.text[:500]}..."  # 截断长文本
            )

    def request(self, method, url, **kwargs):
        """通用请求方法，带日志记录和加解密"""
        # 处理完整URL
        full_url = f"{self.base_url}{url}" if url.startswith("/") else f"{self.base_url}/{url}"
        
        # 请求数据加密
        if self.encrypt_enabled and "json" in kwargs:
            kwargs["json"] = {
                "data": self.crypto.aes_encrypt(json.dumps(kwargs["json"])),
                "timestamp": self.crypto.get_timestamp()
            }
        
        # 记录请求日志
        self._log_request(method, full_url,** kwargs)
        
        # 发送请求
        try:
            response = self.session.request(
                method=method,
                url=full_url,
                headers=self.headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()  # 抛出HTTP错误
        except requests.exceptions.RequestException as e:
            logger.error(f"请求异常：{str(e)}")
            raise
        
        # 记录响应日志
        self._log_response(response)
        
        # 响应数据解密
        try:
            response_data = response.json()
            if self.encrypt_enabled and "data" in response_data:
                decrypted_data = self.crypto.aes_decrypt(response_data["data"])
                response_data["data"] = json.loads(decrypted_data)
            return response_data
        except:
            return {"status_code": response.status_code, "text": response.text}

    def get(self, url,** kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url,** kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url,** kwargs):
        return self.request("PUT", url, **kwargs)

    def delete(self, url,** kwargs):
        return self.request("DELETE", url, **kwargs)
