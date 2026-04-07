#!/usr/bin/env python3
"""
图片恢复脚本 - 宿主机版本
从容器overlay存储中恢复图片并迁移到数据库
"""
import os
import sys
import uuid
import hashlib
import subprocess
from datetime import datetime

# 数据库连接信息
DB_URL = "postgresql://zhanggan:Lily421020%23@pgm-uf6cml154nbjz51y6o.pg.rds.aliyuncs.com:5432/tq"

OVERLAY_BASE = "/var/lib/containers/storage/overlay"


def get_file_md5(file_path: str) -> str:
    """计算文件的MD5哈希值"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def check_image_validity(file_path: str) -> tuple:
    """
    检查图片是否有效
    
    Returns:
        (is_valid, content_type, error_message)
    """
    try:
        with open(file_path, 'rb') as f:
            header = f.read(12)
        
        if len(header) < 8:
            return False, None, "文件太小"
        
        # JPEG
        if header[:3] == b'\xff\xd8\xff':
            return True, "image/jpeg", "JPEG"
        # PNG
        if header[:8] == b'\x89PNG\r\n\x1a\n':
            return True, "image/png", "PNG"
        # GIF
        if header[:4] == b'GIF8':
            return True, "image/gif", "GIF"
        # WebP
        if header[:4] == b'RIFF' and header[8:12] == b'WEBP':
            return True, "image/webp", "WebP"
        
        return False, None, "未知格式"
    except Exception as e:
        return False, None, str(e)


def find_overlay_images() -> list:
    """在overlay存储中查找所有图片文件"""
    images = []
    
    result = subprocess.run(
        ['find', OVERLAY_BASE, '-path', '*uploads*', '-type', 'f'],
        capture_output=True, text=True
    )
    
    for line in result.stdout.strip().split('\n'):
        if not line:
            continue
        
        file_path = line.strip()
        filename = os.path.basename(file_path)
        
        # 只处理图片文件
        if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            continue
        
        # 提取日期目录
        parts = file_path.split('/')
        upload_date = None
        for i, part in enumerate(parts):
            if part == 'uploads' and i + 1 < len(parts):
                upload_date = parts[i + 1]
                break
        
        if upload_date and len(upload_date) == 8 and upload_date.isdigit():
            images.append({
                'file_path': file_path,
                'filename': filename,
                'upload_date': upload_date,
                'relative_path': f'/uploads/{upload_date}/{filename}'
            })
    
    return images


def main():
    """主函数"""
    print("=" * 70)
    print("图片恢复工具 (宿主机版本)")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    try:
        import psycopg2
        from psycopg2.extras import execute_values
    except ImportError:
        print("错误: 需要安装 psycopg2")
        print("运行: pip install psycopg2-binary")
        return
    
    # 连接数据库
    print("\n[1/4] 连接数据库...")
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        print("  数据库连接成功")
    except Exception as e:
        print(f"  数据库连接失败: {e}")
        return
    
    # 创建表
    print("\n[2/4] 检查uploaded_file表...")
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS uploaded_file (
                id BIGSERIAL PRIMARY KEY,
                file_id VARCHAR(36) UNIQUE NOT NULL,
                original_filename VARCHAR(255),
                stored_filename VARCHAR(255) NOT NULL,
                content_type VARCHAR(100),
                file_data BYTEA NOT NULL,
                file_size BIGINT NOT NULL,
                file_path VARCHAR(500),
                upload_date VARCHAR(10) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uploaded_file_id ON uploaded_file(file_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uploaded_file_path ON uploaded_file(file_path)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_uploaded_upload_date ON uploaded_file(upload_date)")
        conn.commit()
        print("  表已准备就绪")
    except Exception as e:
        print(f"  创建表失败: {e}")
        return
    
    # 查找图片
    print("\n[3/4] 查找overlay存储中的图片...")
    images = find_overlay_images()
    print(f"  找到 {len(images)} 个图片文件")
    
    # 去重
    unique_images = {}
    for img in images:
        key = img['relative_path']
        if key not in unique_images:
            unique_images[key] = img
    
    images = list(unique_images.values())
    print(f"  去重后: {len(images)} 个唯一图片")
    
    # 迁移图片
    print("\n[4/4] 迁移图片到数据库...")
    success_count = 0
    skip_count = 0
    fail_count = 0
    failed_files = []
    
    for i, img in enumerate(images):
        if (i + 1) % 50 == 0:
            print(f"  进度: {i + 1}/{len(images)}")
        
        try:
            # 检查是否已存在
            cur.execute("SELECT COUNT(*) FROM uploaded_file WHERE file_path = %s", (img['relative_path'],))
            if cur.fetchone()[0] > 0:
                skip_count += 1
                continue
            
            # 检查图片有效性
            is_valid, content_type, msg = check_image_validity(img['file_path'])
            if not is_valid:
                fail_count += 1
                failed_files.append({'path': img['relative_path'], 'error': f'无效图片: {msg}'})
                continue
            
            # 读取文件
            with open(img['file_path'], 'rb') as f:
                file_data = f.read()
            
            file_size = len(file_data)
            file_id = str(uuid.uuid4())
            
            # 插入数据库
            cur.execute("""
                INSERT INTO uploaded_file 
                (file_id, original_filename, stored_filename, content_type, file_data, file_size, file_path, upload_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                file_id, img['filename'], img['filename'], content_type,
                file_data, file_size, img['relative_path'], img['upload_date']
            ))
            conn.commit()
            
            success_count += 1
            
        except Exception as e:
            fail_count += 1
            failed_files.append({'path': img['relative_path'], 'error': str(e)})
    
    # 输出结果
    print("\n" + "=" * 70)
    print("迁移完成")
    print("=" * 70)
    print(f"成功迁移: {success_count}")
    print(f"已存在跳过: {skip_count}")
    print(f"迁移失败: {fail_count}")
    
    if failed_files:
        print("\n失败文件列表:")
        for f in failed_files[:10]:
            print(f"  - {f['path']}: {f['error']}")
        if len(failed_files) > 10:
            print(f"  ... 还有 {len(failed_files) - 10} 个")
    
    # 验证
    print("\n验证迁移结果...")
    cur.execute("SELECT COUNT(*) FROM uploaded_file")
    total_count = cur.fetchone()[0]
    
    cur.execute("SELECT SUM(file_size) FROM uploaded_file")
    total_size = cur.fetchone()[0] or 0
    
    print(f"数据库中现有 {total_count} 条图片记录")
    print(f"总大小: {total_size / 1024 / 1024:.2f} MB")
    
    cur.close()
    conn.close()
    
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
