#!/usr/bin/env python3
"""
测试批量删除接口
"""

import requests
import json

def test_batch_delete():
    url = "http://localhost:1000/api/v1/images/batch"
    
    # 测试数据
    test_data = {
        "image_ids": [60, 59, 58, 57]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"发送请求到: {url}")
    print(f"请求体: {json.dumps(test_data, indent=2)}")
    
    try:
        response = requests.delete(url, json=test_data, headers=headers)
        
        print(f"状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 422:
            print("422 错误详情:")
            try:
                error_detail = response.json()
                print(json.dumps(error_detail, indent=2, ensure_ascii=False))
            except:
                print("无法解析错误响应")
                print(f"原始响应: {response.text}")
        else:
            try:
                result = response.json()
                print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except:
                print(f"无法解析响应: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("连接错误: 请确认后端服务器正在运行")
    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_batch_delete()
