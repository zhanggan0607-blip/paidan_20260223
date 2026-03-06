import requests
import json
from urllib.parse import quote

headers = {'X-User-Name': quote('张干'), 'X-User-Role': quote('管理员')}

# 审批通过工单 165
update_data = {'status': '已完成'}
r = requests.patch('http://localhost:8000/api/v1/spot-work/165', 
                   json=update_data, 
                   headers=headers)
print(f'审批结果: {r.status_code}')
result = r.json()
print(f'返回数据: {json.dumps(result, ensure_ascii=False, indent=2)}')

# 验证状态
r2 = requests.get('http://localhost:8000/api/v1/spot-work/165')
final = r2.json()
print(f'\n最终状态: {final.get("data", {}).get("status")}')
print(f'实际完成日期: {final.get("data", {}).get("actual_completion_date")}')
