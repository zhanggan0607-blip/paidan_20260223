#!/usr/bin/env python
"""
图片恢复脚本 - 容器内版本
从/app/uploads目录恢复图片到数据库
"""
import os
import sys
import uuid
import hashlib
from datetime import datetime

sys.path.insert(0, '/app')
os.chdir('/app')

from sqlalchemy import create_engine, text
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
        (is_valid, content_type, error_message)
    """
    if len(file_data) < 8:
        return False, None, "文件太小"
    
    # JPEG
    if file_data[:3] == b'\xff\xd8\xff':
        return True, "image/jpeg", "JPEG"
    # PNG
    if file_data[:8] == b'\x89PNG\r\n\x1a\n':
        return True, "image/png", "PNG"
    # GIF
    if file_data[:4] == b'GIF8':
        return True, "image/gif", "GIF"
    # WebP
    if file_data[:4] == b'RIFF' and file_data[8:12] == b'WEBP':
        return True, "image/webp", "WebP"
    
    return False, None, "未知格式"


def find_upload_images() -> list:
    """在/app/uploads目录中查找所有图片文件"""
    images = []
    
    if not os.path.exists(UPLOAD_DIR):
        print(f"  上传目录不存在: {UPLOAD_DIR}")
        return images
    
    for date_dir in os.listdir(UPLOAD_DIR):
        date_path = os.path.join(UPLOAD_DIR, date_dir)
        
        if not os.path.isdir(date_path):
            continue
        
        # 检查是否是日期目录 (YYYYMMDD)
        if len(date_dir) != 8 or not date_dir.isdigit():
            continue
        
        for filename in os.listdir(date_path):
            file_path = os.path.join(date_path, filename)
            
            if not os.path.isfile(file_path):
                continue
            
            # 只处理图片文件
            if not filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                continue
            
            images.append({
                'file_path': file_path,
                'filename': filename,
                'upload_date': date_dir,
                'relative_path': f'/uploads/{date_dir}/{filename}'
            })
    
    return images


def check_file_exists(conn, file_path: str) -> bool:
    """检查文件是否已存在于数据库"""
    result = conn.execute(text(
        "SELECT COUNT(*) FROM uploaded_file WHERE file_path = :path"
    ), {'path': file_path})
    return result.scalar() > 0


def migrate_image_to_db(conn, image_info: dict) -> dict:
    """将单个图片迁移到数据库"""
    result = {
        'success': False,
        'file_path': image_info['relative_path'],
        'error': None
    }
    
    try:
        # 检查文件是否已存在
        if check_file_exists(conn, image_info['relative_path']):
            result['error'] = '文件已存在'
            return result
        
        # 读取文件内容
        with open(image_info['file_path'], 'rb') as f:
            file_data = f.read()
        
        # 检查图片有效性
        is_valid, content_type, msg = check_image_validity(file_data)
        if not is_valid:
            result['error'] = f'无效图片: {msg}'
            return result
        
        file_size = len(file_data)
        file_id = str(uuid.uuid4())
        
        # 插入数据库
        insert_sql = """
        INSERT INTO uploaded_file 
        (file_id, original_filename, stored_filename, content_type, file_data, file_size, file_path, upload_date)
        VALUES 
        (:file_id, :original_filename, :stored_filename, :content_type, :file_data, :file_size, :file_path, :upload_date)
        """
        
        conn.execute(text(insert_sql), {
            'file_id': file_id,
            'original_filename': image_info['filename'],
            'stored_filename': image_info['filename'],
            'content_type': content_type,
            'file_data': file_data,
            'file_size': file_size,
            'file_path': image_info['relative_path'],
            'upload_date': image_info['upload_date']
        })
        conn.commit()
        
        result['success'] = True
        result['file_id'] = file_id
        result['file_size'] = file_size
        
    except Exception as e:
        result['error'] = str(e)
    
    return result


def main():
    """主函数"""
    print("=" * 70)
    print("图片恢复工具 (容器内版本)")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    engine = create_engine(db_url)
    
    with engine.connect() as conn:
        # 1. 检查uploaded_file表
        print("\n[1/3] 检查uploaded_file表...")
        table_check = conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_name = 'uploaded_file'
        """))
        tables = [row[0] for row in table_check]
        
        if 'uploaded_file' not in tables:
            print("  表不存在，正在创建...")
            create_sql = """
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
            );
            CREATE INDEX IF NOT EXISTS idx_uploaded_file_id ON uploaded_file(file_id);
            CREATE INDEX IF NOT EXISTS idx_uploaded_file_path ON uploaded_file(file_path);
            CREATE INDEX IF NOT EXISTS idx_uploaded_upload_date ON uploaded_file(upload_date);
            """
            conn.execute(text(create_sql))
            conn.commit()
            print("  uploaded_file 表已创建")
        else:
            print("  表已存在")
        
        # 2. 查找图片
        print("\n[2/3] 查找/app/uploads目录中的图片...")
        images = find_upload_images()
        print(f"  找到 {len(images)} 个图片文件")
        
        # 3. 迁移图片
        print("\n[3/3] 迁移图片到数据库...")
        success_count = 0
        skip_count = 0
        fail_count = 0
        failed_files = []
        
        for i, img in enumerate(images):
            if (i + 1) % 50 == 0:
                print(f"  进度: {i + 1}/{len(images)}")
            
            result = migrate_image_to_db(conn, img)
            
            if result['success']:
                success_count += 1
            elif result['error'] == '文件已存在':
                skip_count += 1
            else:
                fail_count += 1
                failed_files.append({
                    'path': img['relative_path'],
                    'error': result['error']
                })
        
        # 4. 输出结果
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
        
        # 5. 验证
        print("\n验证迁移结果...")
        count_result = conn.execute(text("SELECT COUNT(*) FROM uploaded_file"))
        total_count = count_result.scalar()
        
        size_result = conn.execute(text("SELECT SUM(file_size) FROM uploaded_file"))
        total_size = size_result.scalar() or 0
        
        print(f"数据库中现有 {total_count} 条图片记录")
        print(f"总大小: {total_size / 1024 / 1024:.2f} MB")
        
        # 按日期统计
        date_result = conn.execute(text("""
            SELECT upload_date, COUNT(*), SUM(file_size) 
            FROM uploaded_file 
            GROUP BY upload_date 
            ORDER BY upload_date
        """))
        print("\n按日期统计:")
        for row in date_result:
            print(f"  {row[0]}: {row[1]} 个文件, {row[2] / 1024:.2f} KB")
        
        return {
            'success_count': success_count,
            'skip_count': skip_count,
            'fail_count': fail_count,
            'total_in_db': total_count,
            'total_size': total_size
        }


if __name__ == "__main__":
    result = main()
    print(f"\n完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
