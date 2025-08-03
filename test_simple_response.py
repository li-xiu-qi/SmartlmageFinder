#!/usr/bin/env python3
"""
简单的响应模型修复测试
"""

from backend.global_schemas import ResponseModel

def test_simple_response():
    """测试简单响应"""
    # 测试成功响应
    success_resp = ResponseModel.success(data={"test": "data"}, message="测试成功")
    print("成功响应:")
    print(success_resp.to_dict())
    
    # 测试错误响应
    error_resp = ResponseModel.error(code="TEST_ERROR", message="测试错误")
    print("\n错误响应:")
    print(error_resp.to_dict())

if __name__ == "__main__":
    test_simple_response()
