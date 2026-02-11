import requests
import json

url = "http://localhost:8080/api/v1/project-info"
headers = {"Content-Type": "application/json"}

test_projects = [
    {
        "project_id": "P001",
        "project_name": "北京地铁1号线维保项目",
        "completion_date": "2024-01-01T00:00:00",
        "maintenance_end_date": "2024-12-31T00:00:00",
        "maintenance_period": "每月",
        "client_name": "北京地铁运营有限公司",
        "address": "北京市朝阳区建国路88号",
        "project_abbr": "BJM1",
        "client_contact": "张经理",
        "client_contact_position": "运营总监",
        "client_contact_info": "13800138001"
    },
    {
        "project_id": "P002",
        "project_name": "上海地铁2号线维保项目",
        "completion_date": "2024-02-01T00:00:00",
        "maintenance_end_date": "2024-12-31T00:00:00",
        "maintenance_period": "每周",
        "client_name": "上海地铁运营有限公司",
        "address": "上海市浦东新区世纪大道100号",
        "project_abbr": "SHM2",
        "client_contact": "李总监",
        "client_contact_position": "技术总监",
        "client_contact_info": "13800138002"
    },
    {
        "project_id": "P003",
        "project_name": "广州地铁3号线维保项目",
        "completion_date": "2024-03-01T00:00:00",
        "maintenance_end_date": "2024-12-31T00:00:00",
        "maintenance_period": "每季度",
        "client_name": "广州地铁运营有限公司",
        "address": "广州市天河区天河路200号",
        "project_abbr": "GZM3",
        "client_contact": "王经理",
        "client_contact_position": "项目经理",
        "client_contact_info": "13800138003"
    },
    {
        "project_id": "P004",
        "project_name": "深圳地铁4号线维保项目",
        "completion_date": "2024-04-01T00:00:00",
        "maintenance_end_date": "2024-12-31T00:00:00",
        "maintenance_period": "每天",
        "client_name": "深圳地铁运营有限公司",
        "address": "深圳市福田区深南大道300号",
        "project_abbr": "SZM4",
        "client_contact": "赵总监",
        "client_contact_position": "运营总监",
        "client_contact_info": "13800138004"
    },
    {
        "project_id": "P005",
        "project_name": "成都地铁5号线维保项目",
        "completion_date": "2024-05-01T00:00:00",
        "maintenance_end_date": "2024-12-31T00:00:00",
        "maintenance_period": "每半年",
        "client_name": "成都地铁运营有限公司",
        "address": "成都市锦江区人民南路50号",
        "project_abbr": "CDM5",
        "client_contact": "刘经理",
        "client_contact_position": "技术经理",
        "client_contact_info": "13800138005"
    }
]

for i, project_data in enumerate(test_projects, 1):
    try:
        response = requests.post(url, headers=headers, json=project_data)
        if response.status_code == 201:
            print(f"✅ 创建项目 {i}/5: {project_data['project_id']} - {project_data['project_name']}")
        else:
            print(f"❌ 创建项目 {i}/5 失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 创建项目 {i}/5 失败: {str(e)}")

print("✅ 完成！")