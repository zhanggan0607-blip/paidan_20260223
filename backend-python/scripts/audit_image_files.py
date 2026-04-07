#!/usr/bin/env python
"""
图片文件审计脚本 - 完整版
对比服务器文件系统与数据库记录，生成详细审计报告
"""
import os
import sys
import json
import hashlib
from datetime import datetime
from io import BytesIO

sys.path.insert(0, '/app')
os.chdir('/app')

from sqlalchemy import create_engine, text, func
from dotenv import load_dotenv

load_dotenv('/app/.env')
db_url = os.getenv('DATABASE_URL', '')

UPLOAD_DIR = "/app/uploads"


def get_file_md5(file_data: bytes) -> str:
    """计算文件的MD5哈希值"""
    return hashlib.md5(file_data).hexdigest()


def check_image_validity(file_data: bytes) -> tuple:
    """
    检查图片是否有效
    
    Returns:
        (is_valid, error_message)
    """
    if len(file_data) < 8:
        return False, "文件太小，不是有效的图片"
    
    if file_data[:3] == b'\xff\xd8\xff':
        return True, "JPEG"
    if file_data[:8] == b'\x89PNG\r\n\x1a\n':
        return True, "PNG"
    if file_data[:4] == b'GIF8':
        return True, "GIF"
    if file_data[:4] == b'RIFF' and file_data[8:12] == b'WEBP':
        return True, "WebP"
    
    return False, "未知的图片格式"


def get_table_columns(conn, table_name: str) -> list:
    """获取表的列名"""
    result = conn.execute(text(f"""
        SELECT column_name FROM information_schema.columns 
        WHERE table_name = '{table_name}'
    """))
    return [row[0] for row in result]


def audit_database_images(conn) -> dict:
    """审计数据库中的图片引用"""
    result = {
        "total_references": 0,
        "by_table": {},
        "by_date": {},
        "all_paths": [],
        "missing_tables": [],
    }
    
    tables_to_check = [
        ("temporary_repair", ["photos", "signature"]),
        ("periodic_inspection_record", ["photos", "signature"]),
        ("spot_work", ["photos", "signature"]),
        ("spot_work_worker", ["id_card_front", "id_card_back", "signature"]),
        ("maintenance_log", ["photos", "images"]),
    ]
    
    for table_name, columns in tables_to_check:
        table_columns = get_table_columns(conn, table_name)
        result["by_table"][table_name] = {
            "columns": table_columns,
            "image_columns": [],
            "count": 0,
            "paths": [],
        }
        
        for col in columns:
            if col in table_columns:
                result["by_table"][table_name]["image_columns"].append(col)
                
                try:
                    # 检查记录数
                    count_result = conn.execute(text(f"""
                        SELECT COUNT(*) FROM {table_name} 
                        WHERE {col} IS NOT NULL AND {col} != '' AND {col} != '[]'
                    """))
                    count = count_result.scalar()
                    
                    if count > 0:
                        # 获取路径
                        paths_result = conn.execute(text(f"""
                            SELECT {col} FROM {table_name} 
                            WHERE {col} IS NOT NULL AND {col} != '' AND {col} != '[]'
                        """))
                        
                        for row in paths_result:
                            value = row[0]
                            if value:
                                # 尝试解析JSON数组
                                if value.startswith('['):
                                    try:
                                        paths = json.loads(value)
                                        result["by_table"][table_name]["paths"].extend(paths)
                                        result["all_paths"].extend(paths)
                                    except:
                                        pass
                                else:
                                    result["by_table"][table_name]["paths"].append(value)
                                    result["all_paths"].append(value)
                        
                        result["by_table"][table_name]["count"] += count
                        
                except Exception as e:
                    print(f"  错误检查 {table_name}.{col}: {e}")
    
    # 统计总数和按日期分组
    result["total_references"] = len(result["all_paths"])
    
    for path in result["all_paths"]:
        if path and '/uploads/' in path:
            parts = path.split('/')
            if len(parts) >= 3:
                date = parts[2]
                result["by_date"][date] = result["by_date"].get(date, 0) + 1
    
    return result


def audit_filesystem() -> dict:
    """审计文件系统中的图片文件"""
    result = {
        "exists": os.path.exists(UPLOAD_DIR),
        "total_files": 0,
        "total_size": 0,
        "by_date": {},
        "files": [],
    }
    
    if not result["exists"]:
        return result
    
    for root, dirs, files in os.walk(UPLOAD_DIR):
        for filename in files:
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                file_path = os.path.join(root, filename)
                relative_path = file_path.replace(UPLOAD_DIR, "/uploads")
                
                try:
                    file_size = os.path.getsize(file_path)
                    result["total_files"] += 1
                    result["total_size"] += file_size
                    result["files"].append({
                        "path": relative_path,
                        "size": file_size,
                    })
                    
                    # 按日期分组
                    parts = relative_path.split('/')
                    if len(parts) >= 3:
                        date = parts[2]
                        if date not in result["by_date"]:
                            result["by_date"][date] = {"count": 0, "size": 0}
                        result["by_date"][date]["count"] += 1
                        result["by_date"][date]["size"] += file_size
                        
                except Exception as e:
                    print(f"  错误读取文件 {file_path}: {e}")
    
    return result


def check_uploaded_file_table(conn) -> dict:
    """检查uploaded_file表是否存在及其内容"""
    result = {
        "exists": False,
        "count": 0,
        "total_size": 0,
        "by_date": {},
    }
    
    try:
        # 检查表是否存在
        table_check = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'uploaded_file'
        """))
        tables = [row[0] for row in table_check]
        result["exists"] = 'uploaded_file' in tables
        
        if result["exists"]:
            # 获取记录数
            count_result = conn.execute(text("SELECT COUNT(*) FROM uploaded_file"))
            result["count"] = count_result.scalar()
            
            # 获取总大小
            size_result = conn.execute(text("SELECT SUM(file_size) FROM uploaded_file"))
            result["total_size"] = size_result.scalar() or 0
            
            # 按日期分组
            date_result = conn.execute(text("""
                SELECT upload_date, COUNT(*), SUM(file_size) 
                FROM uploaded_file 
                GROUP BY upload_date
            """))
            for row in date_result:
                result["by_date"][row[0]] = {
                    "count": row[1],
                    "size": row[2],
                }
                
    except Exception as e:
        print(f"  错误检查uploaded_file表: {e}")
    
    return result


def generate_report(db_result: dict, fs_result: dict, uf_result: dict) -> str:
    """生成审计报告"""
    lines = []
    
    lines.append("=" * 70)
    lines.append("图片文件审计报告")
    lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)
    
    # 1. 数据库图片引用统计
    lines.append("\n## 1. 数据库图片引用统计\n")
    lines.append(f"总引用数: {db_result['total_references']}")
    
    lines.append("\n### 按表统计:")
    for table, info in db_result["by_table"].items():
        if info["count"] > 0:
            lines.append(f"  - {table}: {info['count']} 条记录")
            lines.append(f"    图片列: {info['image_columns']}")
    
    lines.append("\n### 按日期统计:")
    for date, count in sorted(db_result["by_date"].items()):
        lines.append(f"  - {date}: {count} 个图片")
    
    # 2. 文件系统统计
    lines.append("\n## 2. 文件系统统计\n")
    lines.append(f"上传目录存在: {fs_result['exists']}")
    lines.append(f"总文件数: {fs_result['total_files']}")
    lines.append(f"总大小: {fs_result['total_size'] / 1024 / 1024:.2f} MB")
    
    if fs_result["by_date"]:
        lines.append("\n### 按日期统计:")
        for date, info in sorted(fs_result["by_date"].items()):
            lines.append(f"  - {date}: {info['count']} 个文件, {info['size'] / 1024:.2f} KB")
    
    # 3. uploaded_file表统计
    lines.append("\n## 3. uploaded_file表统计\n")
    lines.append(f"表存在: {uf_result['exists']}")
    
    if uf_result["exists"]:
        lines.append(f"记录数: {uf_result['count']}")
        lines.append(f"总大小: {uf_result['total_size'] / 1024 / 1024:.2f} MB")
        
        if uf_result["by_date"]:
            lines.append("\n### 按日期统计:")
            for date, info in sorted(uf_result["by_date"].items()):
                lines.append(f"  - {date}: {info['count']} 条记录, {info['size'] / 1024:.2f} KB")
    
    # 4. 差异分析
    lines.append("\n## 4. 差异分析\n")
    
    # 找出数据库引用但文件不存在的图片
    db_paths = set(db_result["all_paths"])
    fs_paths = set(f["path"] for f in fs_result["files"])
    
    missing_files = db_paths - fs_paths
    orphan_files = fs_paths - db_paths
    
    lines.append(f"数据库引用但文件缺失: {len(missing_files)} 个")
    lines.append(f"文件存在但无数据库引用: {len(orphan_files)} 个")
    
    if missing_files:
        lines.append("\n### 缺失文件列表 (前20个):")
        for path in sorted(missing_files)[:20]:
            lines.append(f"  - {path}")
        if len(missing_files) > 20:
            lines.append(f"  ... 还有 {len(missing_files) - 20} 个")
    
    if orphan_files:
        lines.append("\n### 孤立文件列表 (前20个):")
        for path in sorted(orphan_files)[:20]:
            lines.append(f"  - {path}")
        if len(orphan_files) > 20:
            lines.append(f"  ... 还有 {len(orphan_files) - 20} 个")
    
    # 5. 建议措施
    lines.append("\n## 5. 建议措施\n")
    
    if len(missing_files) > 0:
        lines.append("### 紧急问题: 图片文件丢失")
        lines.append(f"- 发现 {len(missing_files)} 个图片引用指向不存在的文件")
        lines.append("- 可能原因: 容器重启后未挂载持久化存储")
        lines.append("- 建议:")
        lines.append("  1. 检查是否有备份可以恢复")
        lines.append("  2. 创建uploaded_file表并迁移现有文件")
        lines.append("  3. 配置持久化存储避免再次丢失")
    
    if not uf_result["exists"]:
        lines.append("\n### 需要创建uploaded_file表")
        lines.append("- 当前系统未使用数据库存储图片")
        lines.append("- 建议创建uploaded_file表并迁移现有文件")
    
    lines.append("\n" + "=" * 70)
    lines.append("审计完成")
    lines.append("=" * 70)
    
    return "\n".join(lines)


def main():
    """主函数"""
    print("=" * 70)
    print("图片文件审计工具")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # 1. 审计数据库图片引用
        print("\n[1/3] 审计数据库图片引用...")
        db_result = audit_database_images(conn)
        print(f"  找到 {db_result['total_references']} 个图片引用")
        
        # 2. 审计文件系统
        print("\n[2/3] 审计文件系统...")
        fs_result = audit_filesystem()
        print(f"  找到 {fs_result['total_files']} 个文件")
        
        # 3. 检查uploaded_file表
        print("\n[3/3] 检查uploaded_file表...")
        uf_result = check_uploaded_file_table(conn)
        print(f"  表存在: {uf_result['exists']}")
        
        # 4. 生成报告
        print("\n生成审计报告...")
        report = generate_report(db_result, fs_result, uf_result)
        
        # 保存报告
        report_path = f"/app/audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"\n报告已保存到: {report_path}")
        except Exception as e:
            print(f"\n无法保存报告: {e}")
        
        print("\n" + report)
        
        return {
            "database": db_result,
            "filesystem": fs_result,
            "uploaded_file_table": uf_result,
        }


if __name__ == "__main__":
    result = main()
