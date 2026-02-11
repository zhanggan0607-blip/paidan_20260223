import requests
import json

base_url = "http://localhost:8080/api/v1"

def test_api(endpoint, description):
    try:
        response = requests.get(f"{base_url}{endpoint}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {description}")
            if 'data' in data:
                if 'content' in data['data']:
                    print(f"   记录数: {len(data['data']['content'])}")
                elif isinstance(data['data'], list):
                    print(f"   记录数: {len(data['data'])}")
            print()
        else:
            print(f"❌ {description} - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ {description} - {str(e)}")
    print()

print("=" * 60)
print("测试前端所有 API 端点")
print("=" * 60)
print()

test_api("/project-info?page=0&size=10", "项目信息管理 (ProjectInfoManagement.vue)")
test_api("/personnel/all/list", "人员管理 (PersonnelManagement.vue)")
test_api("/personnel?page=0&size=10", "人员列表 (分页)")
test_api("/maintenance-plan?page=0&size=10", "维保计划管理 (MaintenancePlanManagement.vue)")
test_api("/maintenance-plan/all/list", "维保计划列表 (全部)")
test_api("/spare-parts/usage?page=0&size=10", "备品备件领用 (SparePartsIssue.vue)")
test_api("/spare-parts/inbound-records?page=0&size=10", "备品备件入库 (SparePartsStock.vue)")
test_api("/spare-parts/stock", "备品备件库存 (SparePartsManagement.vue)")
test_api("/spare-parts/products", "备品备件产品列表")

print("=" * 60)
print("✅ 所有 API 测试完成")
print("=" * 60)