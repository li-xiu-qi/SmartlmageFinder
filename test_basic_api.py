#!/usr/bin/env python3
"""
测试基础API端点
"""

import requests
import json

def test_basic_api():
    """测试基础API端点"""
    print("测试基础API端点...")
    
    base_url = "http://localhost:10050"
    
    # 测试根端点
    urls_to_test = [
        f"{base_url}/",
        f"{base_url}/api/v1/",
        f"{base_url}/api/v1/system/info"
    ]
    
    for url in urls_to_test:
        try:
            print(f"\n测试: {url}")
            response = requests.get(url, timeout=5)
            print(f"状态码: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                response_data = response.json()
                print(f"响应: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
            else:
                print(f"响应: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"请求超时: {url}")
        except requests.exceptions.RequestException as e:
            print(f"请求异常: {e}")
        except Exception as e:
            print(f"其他异常: {e}")

if __name__ == "__main__":
    test_basic_api()
