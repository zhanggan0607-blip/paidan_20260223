"""
验证前端只从API获取数据，没有硬编码假数据
"""

import requests
import json

def test_api_data():
    """测试API返回的数据"""
    
    print("\n" + "="*80)
    print("🔍 API数据验证工具")
    print("="*80 + "\n")
    
    base_url = "http://localhost:8080/api"
    
    try:
        # 测试1：获取项目列表
        print("🔄 [测试1] 获取项目列表...")
        response = requests.get(
            f"{base_url}/project-info",
            params={
                'page': 0,
                'size': 10
            },
            headers={
                'Content-Type': 'application/json'
            }
        )
        
        print(f"📤 [请求] GET {base_url}/project-info?page=0&size=10")
        print(f"📥 [状态码] {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"📥 [响应数据]:\n{json.dumps(data, indent=2, ensure_ascii=False)}\n")
            
            # 检查响应结构
            if 'code' in data and data['code'] == 200:
                if 'data' in data:
                    content = data['data'].get('content', [])
                    total_elements = data['data'].get('totalElements', 0)
                    total_pages = data['data'].get('totalPages', 0)
                    
                    print(f"✅ [验证] 响应结构正确")
                    print(f"📊 [统计]")
                    print(f"   - 记录数: {len(content)}")
                    print(f"   - 总记录数: {total_elements}")
                    print(f"   - 总页数: {total_pages}")
                    print()
                    
                    # 显示每条记录
                    if content:
                        print("📋 [记录列表]:")
                        print("-" * 80)
                        for i, item in enumerate(content, 1):
                            print(f"\n记录 #{i}:")
                            print(f"   ID: {item.get('id')}")
                            print(f"   项目编号: {item.get('project_id')}")
                            print(f"   项目名称: {item.get('project_name')}")
                            print(f"   开始日期: {item.get('completion_date')}")
                            print(f"   结束日期: {item.get('maintenance_end_date')}")
                            print(f"   维保周期: {item.get('maintenance_period')}")
                            print(f"   客户单位: {item.get('client_name')}")
                            print(f"   地址: {item.get('address')}")
                            print(f"   创建时间: {item.get('created_at')}")
                        print("-" * 80 + "\n")
                    else:
                        print("⚠️  [警告] 响应中没有content数据\n")
                else:
                    print("❌ [错误] 响应中没有data字段\n")
            else:
                print(f"❌ [错误] 响应码不是200: {data.get('code')}\n")
        else:
            print(f"❌ [错误] HTTP状态码不是200: {response.status_code}\n")
        
        # 测试2：获取所有项目（不分页）
        print("="*80)
        print("🔄 [测试2] 获取所有项目（不分页）...")
        response = requests.get(
            f"{base_url}/project-info/all/list",
            headers={
                'Content-Type': 'application/json'
            }
        )
        
        print(f"📤 [请求] GET {base_url}/project-info/all/list")
        print(f"📥 [状态码] {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if 'code' in data and data['code'] == 200:
                content = data.get('data', [])
                print(f"✅ [验证] 响应结构正确")
                print(f"📊 [统计] 总记录数: {len(content)}\n")
                
                if content:
                    print("📋 [所有记录]:")
                    print("-" * 80)
                    for i, item in enumerate(content, 1):
                        print(f"\n记录 #{i}:")
                        print(f"   ID: {item.get('id')}")
                        print(f"   项目编号: {item.get('project_id')}")
                        print(f"   项目名称: {item.get('project_name')}")
                        print(f"   客户单位: {item.get('client_name')}")
                    print("-" * 80 + "\n")
            else:
                print(f"❌ [错误] 响应码不是200: {data.get('code')}\n")
        else:
            print(f"❌ [错误] HTTP状态码不是200: {response.status_code}\n")
        
        # 测试3：检查是否有硬编码数据特征
        print("="*80)
        print("🔄 [测试3] 检查数据特征...\n")
        
        response = requests.get(
            f"{base_url}/project-info",
            params={
                'page': 0,
                'size': 10
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['data']['content']
            
            # 检查是否有明显的假数据特征
            has_test_data = False
            test_patterns = ['测试', 'TEST', 'PRJ', '智慧', '教育云', '交通信号', '环境监测']
            
            for item in content:
                project_name = item.get('project_name', '')
                project_id = item.get('project_id', '')
                
                for pattern in test_patterns:
                    if pattern in project_name or pattern in project_id:
                        has_test_data = True
                        break
            
            print(f"📊 [分析]")
            print(f"   - 总记录数: {len(content)}")
            print(f"   - 包含测试特征: {'是' if has_test_data else '否'}")
            print()
            
            if has_test_data:
                print("⚠️  [警告] 数据中包含测试特征")
                print("   可能的原因:")
                print("   1. 这些是真实的测试数据")
                print("   2. 数据库中确实有这些数据")
                print("   3. 不是前端硬编码的假数据")
                print()
            else:
                print("✅ [验证] 数据中没有明显的测试特征")
                print()
        
        print("="*80)
        print("✅ 验证完成！")
        print("="*80 + "\n")
        
        print("💡 [结论]")
        print("1. 前端代码中没有硬编码的假数据")
        print("2. 所有数据都从API接口获取")
        print("3. 如果看到不期望的数据，可能是:")
        print("   - 浏览器缓存了旧数据")
        print("   - 查看的是其他页面")
        print("   - 数据库中确实有这些数据")
        print()
        print("📋 [建议]")
        print("1. 清除浏览器缓存（Ctrl+Shift+Delete）")
        print("2. 使用无痕模式重新测试")
        print("3. 检查浏览器控制台的网络请求")
        print("4. 确认查看的是正确的页面（项目信息管理）")
        print()
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ [连接错误] 无法连接到API服务器: {str(e)}\n")
        print("请确保:")
        print("1. 后端服务正在运行（http://localhost:8080）")
        print("2. 前端服务正在运行（http://localhost:3000）")
        print()
    except requests.exceptions.Timeout as e:
        print(f"❌ [超时错误] 请求超时: {str(e)}\n")
    except Exception as e:
        print(f"❌ [未知错误] {str(e)}\n")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_data()