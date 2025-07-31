from jsonschema import validate, ValidationError
from utils.config_utils import load_schema
from utils.log_utils import logger

def assert_response_success(response):
    """断言响应成功（默认code=200, message=success）"""
    assert response is not None, "响应为空"
    assert "code" in response, "响应中无code字段"
    assert response["code"] == 200, f"响应码非200，实际为: {response['code']}"
    
    if "message" in response:
        assert response["message"] in ["success", "操作成功"], \
            f"响应消息非成功状态: {response['message']}"

def assert_response_code(response, expected_code):
    """断言响应码"""
    assert response is not None, "响应为空"
    assert "code" in response, "响应中无code字段"
    assert response["code"] == expected_code, \
        f"响应码不匹配，预期: {expected_code}, 实际: {response['code']}"

def assert_response_contains(response, expected_data):
    """断言响应包含指定数据"""
    assert response is not None, "响应为空"
    
    if isinstance(expected_data, dict):
        for key, value in expected_data.items():
            assert key in response, f"响应中无字段: {key}"
            assert response[key] == value, \
                f"字段值不匹配，字段: {key}, 预期: {value}, 实际: {response[key]}"
    elif isinstance(expected_data, list):
        for item in expected_data:
            assert item in response, f"响应中无元素: {item}"
    else:
        assert expected_data in str(response), f"响应中无数据: {expected_data}"

def assert_schema_match(response, schema_name):
    """验证响应是否符合JSON Schema"""
    try:
        schema = load_schema(schema_name)
        validate(instance=response, schema=schema)
        logger.info(f"Schema验证通过: {schema_name}")
    except ValidationError as e:
        logger.error(f"Schema验证失败: {str(e)}")
        raise AssertionError(f"响应不符合Schema规范: {schema_name}, 错误: {str(e)}")

def assert_db_record_exists(db_client, sql, params=None, min_count=1):
    """断言数据库记录存在"""
    result = db_client.execute_sql(sql, params)
    assert len(result) >= min_count, \
        f"数据库记录不足，预期至少{min_count}条，实际{len(result)}条，SQL: {sql}"
    return result

def assert_redis_key_exists(redis_client, key, expected_value=None):
    """断言Redis键存在，可选验证值"""
    value = redis_client.get(key)
    assert value is not None, f"Redis键不存在: {key}"
    
    if expected_value is not None:
        assert value == expected_value, \
            f"Redis值不匹配，键: {key}, 预期: {expected_value}, 实际: {value}"
    return value
