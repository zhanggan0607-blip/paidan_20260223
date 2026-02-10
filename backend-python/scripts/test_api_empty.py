import requests
import json

print("=" * 80)
print("测试维保计划API")
print("=" * 80)

base_url = "http://localhost:8080/api/v1/maintenance-plan"

print("\n1. 测试分页查询")
print("-" * 80)

try:
    r = requests.get(base_url, params={'page': 0, 'size': 20}, timeout=10)
    print(f"状态码: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        print(f"✅ 查询成功")
        print(f"总记录数: {data['data']['totalElements']}")
        print(f"当前页记录数: {len(data['data']['content'])}")
        
        if data['data']['totalElements'] == 0:
            print("\n✅ 数据库确实是空的，前端应该显示0条记录")
            print("\n如果前端仍然显示12条数据，可能的原因:")
            print("1. 浏览器缓存 - 请按 Ctrl+F5 强制刷新")
            print("2. 前端代码中有模拟数据")
            print("3. 前端连接的是另一个数据库")
        else:
            print(f"\n⚠️  数据库中有 {data['data']['totalElements']} 条记录")
            print("\n这表明后端返回的数据与数据库不一致")
    else:
        print(f"❌ 查询失败: {r.text}")
        
except Exception as e:
    print(f"❌ 请求异常: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
