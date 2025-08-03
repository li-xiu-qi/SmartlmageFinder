#!/usr/bin/env python3
"""
测试图片更新API端点
"""

import requests

def test_image_update_api():
    """测试图片更新API"""
    print("测试图片更新API...")
    
    # API端点
    base_url = "http://localhost:10050"
    image_id = 1  # 使用我们知道存在的图片ID
    url = f"{base_url}/api/v1/images/{image_id}"
    
    # 测试数据 - 使用FormData格式
    form_data = {
        'description': '这是通过API测试更新的描述'
    }
    
    try:
        print(f"请求URL: {url}")
        print(f"请求数据: {form_data}")
        
        # 发送PATCH请求，使用form数据
        response = requests.patch(
            url, 
            data=form_data,  # 使用data参数发送form数据
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            response_data = response.json()
            print(f"响应数据: {response_data}")
        else:
            print(f"响应内容 (非JSON): {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"其他异常: {e}")

if __name__ == "__main__":
    test_image_update_api()
