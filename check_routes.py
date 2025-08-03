#!/usr/bin/env python3
"""
检查API路由
"""

from main import app

def check_routes():
    print("检查API路由...")
    print("=" * 50)
    
    for route in app.routes:
        methods = getattr(route, 'methods', set())
        if hasattr(route, 'path'):
            print(f"{route.path} - {methods}")
    
    print("=" * 50)
    print("检查完成")

if __name__ == "__main__":
    check_routes()
