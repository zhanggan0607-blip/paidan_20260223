#!/usr/bin/env python
"""
通过API检查服务器数据库结构
"""
import json
import urllib.request
from datetime import datetime

SERVER_URL = "http://8.153.93.123:8000"

def fetch_api(url: str, timeout: int = 15) -> dict:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return {"error": str(e)}

print("=" * 60)
print("通过API检查服务器数据库结构")
print("=" * 60)

print("\n1. 健康检查...")
health = fetch_api(f"{SERVER_URL}/health")
print(f"   状态: {health}")

print("\n2. 获取OpenAPI文档...")
openapi = fetch_api(f"{SERVER_URL}/api/openapi.json")
if "error" not in openapi:
    print(f"   API标题: {openapi.get('info', {}).get('title')}")
    print(f"   API版本: {openapi.get('info', {}).get('version')}")
    paths = list(openapi.get("paths", {}).keys())
    print(f"   API路径数量: {len(paths)}")
    
    schemas = openapi.get("components", {}).get("schemas", {})
    print(f"   数据模型数量: {len(schemas)}")
    
    print("\n3. 数据模型列表:")
    for name, schema in schemas.items():
        if name.endswith("Response") or name.endswith("Request") or name.endswith("Base"):
            continue
        properties = schema.get("properties", {})
        if properties:
            print(f"   {name}: {len(properties)} 个字段")
            for prop, details in list(properties.items())[:5]:
                prop_type = details.get("type", "unknown")
                print(f"      - {prop}: {prop_type}")
            if len(properties) > 5:
                print(f"      ... 还有 {len(properties) - 5} 个字段")

print("\n4. 测试关键API端点...")

endpoints_to_test = [
    "/api/v1/personnel",
    "/api/v1/project-info",
    "/api/v1/maintenance-plan",
    "/api/v1/periodic-inspection",
    "/api/v1/temporary-repair",
    "/api/v1/spot-work",
    "/api/v1/dictionary",
]

for endpoint in endpoints_to_test:
    result = fetch_api(f"{SERVER_URL}{endpoint}")
    if "error" in result:
        print(f"   {endpoint}: 错误 - {result['error'][:50]}")
    else:
        total = result.get("total", "N/A")
        print(f"   {endpoint}: 总数 {total}")

print("\n5. 检查字典数据（状态常量）...")
dict_result = fetch_api(f"{SERVER_URL}/api/v1/dictionary?type=status")
if "data" in dict_result:
    statuses = [d.get("dict_value") for d in dict_result["data"]]
    print(f"   状态值: {statuses}")

print("\n" + "=" * 60)
print("检查完成!")
print("=" * 60)
