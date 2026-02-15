import requests
import random
from datetime import datetime, timedelta
import string

BASE_URL = "http://localhost:8080/api/v1"

SPARE_PARTS_NAMES = [
    "电缆线", "接线端子", "空气开关", "漏电保护器", "继电器",
    "接触器", "热继电器", "按钮开关", "指示灯", "行程开关",
    "接近开关", "光电开关", "温度传感器", "压力传感器", "流量传感器",
    "变频器", "PLC模块", "触摸屏", "伺服电机", "步进电机",
    "减速机", "联轴器", "轴承", "密封圈", "O型圈",
    "液压油", "润滑油", "冷却液", "清洗剂", "防锈剂",
    "焊条", "焊丝", "切割片", "砂轮片", "钻头",
    "丝锥", "板牙", "铣刀", "车刀", "磨头",
    "螺丝", "螺母", "垫片", "弹簧垫圈", "开口销",
    "电缆接头", "线槽", "线管", "扎带", "绝缘胶带"
]

SPARE_PARTS_BRANDS = [
    "西门子", "施耐德", "ABB", "欧姆龙", "三菱",
    "台达", "正泰", "德力西", "上海人民", "常熟开关",
    "富士", "安川", "松下", "基恩士", "倍加福",
    "图尔克", "巴鲁夫", "易福门", "SICK", "劳易测",
    "国产优质", "进口原装", "合资品牌", "定制", "通用"
]

SPARE_PARTS_UNITS = ["件", "个", "只", "套", "米", "公斤", "升", "卷", "盒", "包"]

SUPPLIERS = [
    "上海电气设备有限公司", "北京工业物资有限公司", "广州机电贸易有限公司",
    "深圳自动化科技有限公司", "杭州电气批发中心", "南京工业品供应商",
    "成都机电设备公司", "武汉五金交电公司", "西安工业物资公司", "重庆机电市场"
]

TOOL_NAMES = [
    "万用表", "钳形电流表", "绝缘电阻测试仪", "接地电阻测试仪", "示波器",
    "信号发生器", "频谱分析仪", "红外测温仪", "激光测距仪", "水平仪",
    "电钻", "冲击钻", "角磨机", "切割机", "电焊机",
    "气焊设备", "台钻", "砂轮机", "抛光机", "热风枪",
    "扳手套装", "螺丝刀套装", "内六角扳手套装", "扭力扳手", "管钳",
    "剥线钳", "压线钳", "电缆剪", "钢丝钳", "尖嘴钳",
    "电烙铁", "热缩枪", "标签机", "测电笔", "验电器",
    "绝缘手套", "绝缘鞋", "安全帽", "防护眼镜", "防尘口罩",
    "工具箱", "工具车", "工作台", "零件盒", "磁性工具架"
]

TOOL_CATEGORIES = [
    "测量工具", "电动工具", "焊接工具", "手动工具", "专用工具",
    "安全防护", "存储设备", "检测仪器", "维修设备", "辅助工具"
]

TOOL_SPECIFICATIONS = [
    "3-6mm", "6-10mm", "10-14mm", "14-22mm", "22-32mm",
    "数字显示", "指针式", "高精度", "工业级", "家用级",
    "便携式", "台式", "手持式", "充电式", "插电式",
    "小型", "中型", "大型", "超大型", "定制"
]

LOCATIONS = [
    "A区工具柜1号", "A区工具柜2号", "B区工具柜1号", "B区工具柜2号",
    "维修车间1号柜", "维修车间2号柜", "仓库A区", "仓库B区",
    "电工房", "机修间", "配电室", "控制室"
]


def get_personnel_list():
    response = requests.get(f"{BASE_URL}/personnel/all/list")
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            return data.get('data', [])
    return []


def get_project_list():
    response = requests.get(f"{BASE_URL}/project-info/all/list")
    if response.status_code == 200:
        data = response.json()
        if data.get('code') == 200:
            return data.get('data', [])
    return []


def generate_inbound_no():
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices(string.digits, k=4))
    return f"IN{timestamp}{random_str}"


def generate_tool_id(index):
    return f"TOOL{index:06d}"


def random_date(start_year=2024, end_year=2026):
    start_date = datetime(start_year, 1, 1)
    end_date = datetime(end_year, 12, 31)
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)


def create_spare_parts_inbound(personnel_list, count):
    print(f"\n=== 生成备品备件入库记录 ({count}条) ===")
    success_count = 0
    
    for i in range(count):
        product_name = random.choice(SPARE_PARTS_NAMES)
        brand = random.choice(SPARE_PARTS_BRANDS)
        model = f"型号{random.randint(100, 999)}"
        quantity = random.randint(1, 50)
        unit = random.choice(SPARE_PARTS_UNITS)
        supplier = random.choice(SUPPLIERS)
        user_name = random.choice(personnel_list)['name'] if personnel_list else "测试用户"
        remarks = random.choice(["常规入库", "紧急采购", "补充库存", "新项目备件", ""])
        
        data = {
            "product_name": product_name,
            "brand": brand,
            "model": model,
            "quantity": quantity,
            "unit": unit,
            "supplier": supplier,
            "user_name": user_name,
            "remarks": remarks
        }
        
        try:
            response = requests.post(f"{BASE_URL}/spare-parts/inbound", json=data)
            if response.status_code == 201:
                result = response.json()
                if result.get('code') == 200:
                    success_count += 1
                    if success_count % 10 == 0:
                        print(f"  已成功创建 {success_count} 条入库记录...")
        except Exception as e:
            print(f"  创建入库记录失败: {e}")
    
    print(f"  备品备件入库记录创建完成: 成功 {success_count}/{count} 条")
    return success_count


def create_spare_parts_usage(personnel_list, project_list, count):
    print(f"\n=== 生成备品备件领用记录 ({count}条) ===")
    success_count = 0
    
    products_response = requests.get(f"{BASE_URL}/spare-parts/stock")
    products = []
    if products_response.status_code == 200:
        data = products_response.json()
        if data.get('code') == 200:
            products = data.get('data', {}).get('items', [])
    
    if not products:
        print("  没有可用的备品备件库存，跳过领用记录生成")
        return 0
    
    for i in range(count):
        product = random.choice(products)
        user_name = random.choice(personnel_list)['name'] if personnel_list else "测试用户"
        
        project = random.choice(project_list) if project_list else None
        project_id = project.get('project_id', '') if project else ''
        project_name = project.get('project_name', '') if project else ''
        
        max_quantity = min(product.get('quantity', 10), 10)
        quantity = random.randint(1, max(1, max_quantity))
        
        issue_date = random_date()
        
        data = {
            "product_name": product.get('productName', ''),
            "brand": product.get('brand', ''),
            "model": product.get('model', ''),
            "quantity": quantity,
            "unit": product.get('unit', '件'),
            "user_name": user_name,
            "issue_time": issue_date.strftime('%Y-%m-%d %H:%M:%S'),
            "project_id": project_id,
            "project_name": project_name
        }
        
        try:
            response = requests.post(f"{BASE_URL}/spare-parts/usage", json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('code') == 200:
                    success_count += 1
                    if success_count % 10 == 0:
                        print(f"  已成功创建 {success_count} 条领用记录...")
        except Exception as e:
            print(f"  创建领用记录失败: {e}")
    
    print(f"  备品备件领用记录创建完成: 成功 {success_count}/{count} 条")
    return success_count


def create_repair_tools_stock(count):
    print(f"\n=== 生成维修工具库存 ({count}条) ===")
    success_count = 0
    
    for i in range(count):
        tool_name = random.choice(TOOL_NAMES)
        category = random.choice(TOOL_CATEGORIES)
        specification = random.choice(TOOL_SPECIFICATIONS)
        unit = random.choice(["个", "把", "套", "台", "件"])
        stock = random.randint(1, 20)
        min_stock = random.randint(1, 5)
        location = random.choice(LOCATIONS)
        remark = random.choice(["常用工具", "专用工具", "借出频繁", "新购入", ""])
        
        data = {
            "tool_name": tool_name,
            "category": category,
            "specification": specification,
            "unit": unit,
            "stock": stock,
            "min_stock": min_stock,
            "location": location,
            "remark": remark
        }
        
        try:
            response = requests.post(f"{BASE_URL}/repair-tools/stock", json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('code') == 200:
                    success_count += 1
                    if success_count % 10 == 0:
                        print(f"  已成功创建 {success_count} 条工具库存...")
        except Exception as e:
            print(f"  创建工具库存失败: {e}")
    
    print(f"  维修工具库存创建完成: 成功 {success_count}/{count} 条")
    return success_count


def create_repair_tools_issue(personnel_list, project_list, count):
    print(f"\n=== 生成维修工具领用记录 ({count}条) ===")
    success_count = 0
    
    tools_response = requests.get(f"{BASE_URL}/repair-tools/stock?size=100")
    tools = []
    if tools_response.status_code == 200:
        data = tools_response.json()
        if data.get('code') == 200:
            tools = data.get('data', {}).get('items', [])
    
    if not tools:
        print("  没有可用的维修工具库存，跳过领用记录生成")
        return 0
    
    for i in range(count):
        tool = random.choice(tools)
        user_name = random.choice(personnel_list)['name'] if personnel_list else "测试用户"
        
        project = random.choice(project_list) if project_list else None
        project_id = project.get('id') if project else None
        project_name = project.get('project_name', '') if project else ''
        
        max_quantity = min(tool.get('stock', 5), 3)
        quantity = random.randint(1, max(1, max_quantity))
        
        issue_date = random_date()
        
        data = {
            "tool_id": str(tool.get('id', '')),
            "tool_name": tool.get('tool_name', ''),
            "specification": tool.get('specification', ''),
            "quantity": quantity,
            "user_id": None,
            "user_name": user_name,
            "project_id": project_id,
            "project_name": project_name,
            "remark": random.choice(["项目使用", "临时借用", "维修使用", ""])
        }
        
        try:
            response = requests.post(f"{BASE_URL}/repair-tools/issue", json=data)
            if response.status_code in [200, 201]:
                result = response.json()
                if result.get('code') == 200:
                    success_count += 1
                    if success_count % 10 == 0:
                        print(f"  已成功创建 {success_count} 条工具领用记录...")
        except Exception as e:
            print(f"  创建工具领用记录失败: {e}")
    
    print(f"  维修工具领用记录创建完成: 成功 {success_count}/{count} 条")
    return success_count


def main():
    print("=" * 60)
    print("备品备件和维修工具测试数据生成脚本")
    print("=" * 60)
    
    print("\n正在获取人员和项目数据...")
    personnel_list = get_personnel_list()
    project_list = get_project_list()
    
    print(f"  人员数量: {len(personnel_list)}")
    print(f"  项目数量: {len(project_list)}")
    
    if not personnel_list:
        print("警告: 没有获取到人员数据，将使用默认用户名")
    
    inbound_count = random.randint(20, 100)
    usage_count = random.randint(20, 100)
    tools_stock_count = random.randint(20, 100)
    tools_issue_count = random.randint(20, 100)
    
    print(f"\n计划生成数据:")
    print(f"  - 备品备件入库记录: {inbound_count} 条")
    print(f"  - 备品备件领用记录: {usage_count} 条")
    print(f"  - 维修工具库存: {tools_stock_count} 条")
    print(f"  - 维修工具领用记录: {tools_issue_count} 条")
    
    inbound_success = create_spare_parts_inbound(personnel_list, inbound_count)
    usage_success = create_spare_parts_usage(personnel_list, project_list, usage_count)
    tools_stock_success = create_repair_tools_stock(tools_stock_count)
    tools_issue_success = create_repair_tools_issue(personnel_list, project_list, tools_issue_count)
    
    print("\n" + "=" * 60)
    print("数据生成完成!")
    print("=" * 60)
    print(f"备品备件入库记录: {inbound_success}/{inbound_count} 条")
    print(f"备品备件领用记录: {usage_success}/{usage_count} 条")
    print(f"维修工具库存: {tools_stock_success}/{tools_stock_count} 条")
    print(f"维修工具领用记录: {tools_issue_success}/{tools_issue_count} 条")
    print("=" * 60)


if __name__ == "__main__":
    main()
