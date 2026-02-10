import requests
import json

print("=" * 80)
print("验证维保计划数据同步")
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
        print(f"总页数: {data['data']['totalPages']}")
        print(f"当前页记录数: {len(data['data']['content'])}")
        print(f"当前页: {data['data']['number'] + 1}")
        print(f"每页大小: {data['data']['size']}")
        
        print("\n2. 显示所有记录")
        print("-" * 80)
        
        records = data['data']['content']
        print(f"\n{'ID':<5} {'计划编号':<15} {'计划名称':<20} {'项目编号':<10} {'计划类型':<10} {'设备名称':<15} {'计划状态':<10} {'执行状态':<10} {'完成率':<10}")
        print("-" * 115)
        
        for record in records:
            print(f"{record['id']:<5} {record['plan_id']:<15} {record['plan_name']:<20} {record['project_id']:<10} {record['plan_type']:<10} {record['equipment_name']:<15} {record['plan_status']:<10} {record['execution_status']:<10} {record['completion_rate']:<10}")
        
        print("\n3. 测试按项目查询")
        print("-" * 80)
        
        project_id = "PRJ001"
        r2 = requests.get(f"{base_url}/project/{project_id}", timeout=10)
        
        if r2.status_code == 200:
            data2 = r2.json()
            print(f"✅ 项目 {project_id} 查询成功")
            print(f"记录数: {len(data2['data'])}")
            
            print("\n4. 测试按状态查询")
            print("-" * 80)
            
            r3 = requests.get(f"{base_url}/all/list", timeout=10)
            
            if r3.status_code == 200:
                data3 = r3.json()
                print(f"✅ 所有记录查询成功")
                print(f"总记录数: {len(data3['data'])}")
                
                print("\n5. 统计分析")
                print("-" * 80)
                
                all_records = data3['data']
                
                status_count = {}
                execution_status_count = {}
                plan_type_count = {}
                project_count = {}
                
                for record in all_records:
                    status = record['plan_status']
                    execution_status = record['execution_status']
                    plan_type = record['plan_type']
                    project_id = record['project_id']
                    
                    status_count[status] = status_count.get(status, 0) + 1
                    execution_status_count[execution_status] = execution_status_count.get(execution_status, 0) + 1
                    plan_type_count[plan_type] = plan_type_count.get(plan_type, 0) + 1
                    project_count[project_id] = project_count.get(project_id, 0) + 1
                
                print("\n按计划状态统计:")
                for status, count in status_count.items():
                    print(f"  {status}: {count} 条")
                
                print("\n按执行状态统计:")
                for status, count in execution_status_count.items():
                    print(f"  {status}: {count} 条")
                
                print("\n按计划类型统计:")
                for plan_type, count in plan_type_count.items():
                    print(f"  {plan_type}: {count} 条")
                
                print("\n按项目统计:")
                for project_id, count in project_count.items():
                    print(f"  {project_id}: {count} 条")
                
                print("\n6. 测试即将到期查询")
                print("-" * 80)
                
                r4 = requests.get(f"{base_url}/upcoming/list", timeout=10)
                
                if r4.status_code == 200:
                    data4 = r4.json()
                    print(f"✅ 即将到期查询成功")
                    print(f"即将到期记录数: {len(data4['data'])}")
                    
                    if len(data4['data']) > 0:
                        print("\n即将到期的维保计划:")
                        print(f"{'计划编号':<15} {'计划名称':<20} {'下次维保日期':<20} {'负责人':<10}")
                        print("-" * 70)
                        
                        for record in data4['data']:
                            print(f"{record['plan_id']:<15} {record['plan_name']:<20} {record['next_maintenance_date']:<20} {record['responsible_person']:<10}")
                
                print("\n" + "=" * 80)
                print("✅ 所有验证测试通过")
                print("=" * 80)
                
            else:
                print(f"❌ 所有记录查询失败: {r3.text}")
        else:
            print(f"❌ 项目查询失败: {r2.text}")
    else:
        print(f"❌ 查询失败: {r.text}")
        
except Exception as e:
    print(f"❌ 请求异常: {e}")
    import traceback
    traceback.print_exc()
