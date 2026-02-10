import requests
import json

API_BASE_URL = "http://localhost:8080/api"

def test_create_project():
    """测试创建项目"""
    print("\n" + "="*60)
    print("🧪 测试创建项目功能")
    print("="*60)
    
    test_data = {
        "project_id": "TEST20260127",
        "project_name": "测试项目20260127",
        "completion_date": "2026-01-27T00:00:00",
        "maintenance_end_date": "2027-01-27T00:00:00",
        "maintenance_period": "每月",
        "client_name": "测试客户单位",
        "address": "测试客户地址",
        "project_abbr": "TEST",
        "client_contact": "张三",
        "client_contact_position": "经理",
        "client_contact_info": "13800138000"
    }
    
    print(f"\n📤 [测试数据] {json.dumps(test_data, ensure_ascii=False, indent=2)}")
    
    try:
        print(f"\n📤 [发送请求] POST {API_BASE_URL}/project-info")
        response = requests.post(
            f"{API_BASE_URL}/project-info",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📥 [响应状态码] {response.status_code}")
        print(f"📥 [响应头] {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"\n📥 [响应数据] {json.dumps(response_data, ensure_ascii=False, indent=2)}")
        except:
            print(f"\n📥 [响应文本] {response.text}")
        
        if response.status_code == 201:
            print("\n✅ [成功] 项目创建成功！")
            
            # 验证数据是否在数据库中
            print(f"\n🔍 [验证] 检查项目是否在数据库中...")
            verify_response = requests.get(
                f"{API_BASE_URL}/project-info/all/list",
                timeout=10
            )
            
            if verify_response.status_code == 200:
                verify_data = verify_response.json()
                projects = verify_data.get('data', [])
                
                found = False
                for project in projects:
                    if project.get('project_id') == test_data['project_id']:
                        found = True
                        print(f"\n✅ [验证成功] 项目 {test_data['project_id']} 已在数据库中！")
                        print(f"   - 项目ID: {project.get('id')}")
                        print(f"   - 项目名称: {project.get('project_name')}")
                        break
                
                if not found:
                    print(f"\n❌ [验证失败] 项目 {test_data['project_id']} 未在数据库中！")
            else:
                print(f"\n❌ [验证失败] 无法获取项目列表: {verify_response.status_code}")
                
        else:
            print(f"\n❌ [失败] 创建失败，状态码: {response.status_code}")
            try:
                error_data = response.json()
                print(f"📥 [错误信息] {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"📥 [错误文本] {response.text}")
                
    except requests.exceptions.Timeout:
        print("\n❌ [超时] 请求超时（10秒）")
    except requests.exceptions.ConnectionError:
        print("\n❌ [连接错误] 无法连接到服务器")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ [请求错误] {str(e)}")
    except Exception as e:
        print(f"\n❌ [未知错误] {str(e)}")
    
    print("\n" + "="*60)

def test_get_projects():
    """测试获取项目列表"""
    print("\n" + "="*60)
    print("🧪 测试获取项目列表功能")
    print("="*60)
    
    try:
        print(f"\n📤 [发送请求] GET {API_BASE_URL}/project-info?page=0&size=10")
        response = requests.get(
            f"{API_BASE_URL}/project-info?page=0&size=10",
            timeout=10
        )
        
        print(f"\n📥 [响应状态码] {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"\n📥 [响应数据] {json.dumps(response_data, ensure_ascii=False, indent=2)}")
            
            data = response_data.get('data', {})
            content = data.get('content', [])
            total = data.get('totalElements', 0)
            
            print(f"\n✅ [成功] 获取到 {len(content)} 条记录，共 {total} 条")
            
            if content:
                print(f"\n📋 [项目列表]:")
                for i, project in enumerate(content[:3], 1):
                    print(f"   {i}. {project.get('project_id')} - {project.get('project_name')}")
                if len(content) > 3:
                    print(f"   ... 还有 {len(content) - 3} 条记录")
        else:
            try:
                error_data = response.json()
                print(f"📥 [错误信息] {json.dumps(error_data, ensure_ascii=False, indent=2)}")
            except:
                print(f"📥 [错误文本] {response.text}")
                
    except requests.exceptions.Timeout:
        print("\n❌ [超时] 请求超时（10秒）")
    except requests.exceptions.ConnectionError:
        print("\n❌ [连接错误] 无法连接到服务器")
    except requests.exceptions.RequestException as e:
        print(f"\n❌ [请求错误] {str(e)}")
    except Exception as e:
        print(f"\n❌ [未知错误] {str(e)}")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    print("\n" + "🚀"*60)
    print("SSTCP维护系统 - API功能测试")
    print("🚀"*60 + "\n")
    
    # 测试1: 获取项目列表
    test_get_projects()
    
    print("\n")
    
    # 测试2: 创建项目
    test_create_project()
    
    print("\n" + "✅"*60)
    print("测试完成！")
    print("✅"*60 + "\n")