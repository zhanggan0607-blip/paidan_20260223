#!/usr/bin/env python3
"""
将项目信息中的客户数据同步到客户管理表

功能：
1. 从 project_info 表读取所有客户信息
2. 检查客户是否已存在于 customer 表（根据客户单位名称判断）
3. 如果不存在，则插入到 customer 表

字段对应关系：
- project_info.client_name -> customer.name
- project_info.address -> customer.address
- project_info.client_contact -> customer.contact_person
- project_info.client_contact_info -> customer.phone
- project_info.client_contact_position -> customer.contact_position
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
from app.models.project_info import ProjectInfo
from app.models.customer import Customer


def sync_customers():
    """
    同步项目信息中的客户数据到客户管理表
    """
    settings = get_settings()
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        projects = session.query(ProjectInfo).all()
        
        print(f"找到 {len(projects)} 条项目信息记录")
        
        existing_customers = session.query(Customer).all()
        existing_customer_names = {c.name.lower() for c in existing_customers}
        
        print(f"客户管理表已有 {len(existing_customers)} 条客户记录")
        
        new_customers = []
        skipped_count = 0
        
        for project in projects:
            if not project.client_name or not project.client_name.strip():
                skipped_count += 1
                continue
            
            client_name = project.client_name.strip()
            
            if client_name.lower() in existing_customer_names:
                skipped_count += 1
                continue
            
            customer = Customer(
                name=client_name,
                address=project.address.strip() if project.address else None,
                contact_person=project.client_contact.strip() if project.client_contact else None,
                phone=project.client_contact_info.strip() if project.client_contact_info else None,
                contact_position=project.client_contact_position.strip() if project.client_contact_position else None,
                remarks=f"从项目 {project.project_name} 同步",
            )
            
            new_customers.append(customer)
            existing_customer_names.add(client_name.lower())
        
        if new_customers:
            session.add_all(new_customers)
            session.commit()
            print(f"成功同步 {len(new_customers)} 条新客户记录")
        else:
            print("没有需要同步的新客户记录")
        
        print(f"跳过 {skipped_count} 条记录（客户单位为空或已存在）")
        
        return len(new_customers)
        
    except Exception as e:
        session.rollback()
        print(f"同步失败: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    print("=" * 50)
    print("开始同步项目客户数据到客户管理表")
    print("=" * 50)
    
    count = sync_customers()
    
    print("=" * 50)
    print(f"同步完成，共新增 {count} 条客户记录")
    print("=" * 50)
