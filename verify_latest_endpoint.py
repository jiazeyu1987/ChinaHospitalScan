#!/usr/bin/env python3
"""验证/procurement/latest接口是否在代码中正确实现"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def verify_implementation():
    """验证实现"""
    print("正在验证/procurement/latest接口的实现...")

    try:
        # 检查schemas
        from schemas import ProcurementLatestRequest, ProcurementLatestResponse
        print("✅ Schema模型导入成功")

        # 检查数据库函数
        from db import get_latest_procurement_links
        print("✅ 数据库函数导入成功")

        # 检查main.py中的实现
        import main
        app = main.app

        # 检查路由
        routes = []
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                routes.append(f"{list(route.methods)[0]} {route.path}")

        latest_routes = [r for r in routes if '/procurement/latest' in r]
        if latest_routes:
            print(f"✅ 找到latest接口路由: {latest_routes}")
        else:
            print("❌ 未找到/procurement/latest路由")
            return False

        # 检查OpenAPI
        openapi_schema = app.openapi()
        if '/procurement/latest' in openapi_schema.get('paths', {}):
            print("✅ /procurement/latest在OpenAPI规范中")

            # 获取接口详情
            path_info = openapi_schema['paths']['/procurement/latest']
            if 'post' in path_info:
                post_info = path_info['post']
                print(f"✅ 接口方法: POST")
                print(f"✅ 接口摘要: {post_info.get('summary', 'N/A')}")
                print(f"✅ 接口描述: {post_info.get('description', 'N/A')[:100]}...")

                # 检查参数
                if 'requestBody' in post_info:
                    print("✅ 包含请求体参数")

                return True
            else:
                print("❌ 未找到POST方法")
                return False
        else:
            print("❌ /procurement/latest不在OpenAPI规范中")
            return False

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if verify_implementation():
        print("\n🎉 /procurement/latest接口已正确实现并应在Swagger中显示！")
    else:
        print("\n💥 实现验证失败")