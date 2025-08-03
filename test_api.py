#!/usr/bin/env python3
"""
测试元数据API端点
"""

import requests
import json

def test_metadata_api():
    """测试元数据更新API"""
    print("测试元数据更新API...")
    
    # API端点
    base_url = "http://localhost:10050"
    image_id = 1  # 使用我们知道存在的图片ID
    url = f"{base_url}/api/v1/metadata/{image_id}/update"
    
    # 测试数据
    test_data = {
        "metadata": {
            "test_api": "api_test_value",
            "camera": "Test Camera",
            "iso": "800"
        }
    }
    
    try:
        print(f"请求URL: {url}")
        print(f"请求数据: {json.dumps(test_data, indent=2)}")
        
        # 发送PUT请求
        response = requests.put(
            url, 
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"响应内容 (非JSON): {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"其他异常: {e}")

if __name__ == "__main__":
    test_metadata_api()
