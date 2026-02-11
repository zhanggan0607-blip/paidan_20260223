from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.dictionary import Dictionary
from app.database import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_dictionary_data():
    """初始化字典数据"""
    db = SessionLocal()
    
    try:
        Base.metadata.create_all(bind=engine, checkfirst=True)
        
        dictionary_data = [
            # 临时维修单状态
            {'dict_type': 'temporary_repair_status', 'dict_key': 'not_started', 'dict_value': '未进行', 'dict_label': '未进行', 'sort_order': 1},
            {'dict_type': 'temporary_repair_status', 'dict_key': 'in_progress', 'dict_value': '进行中', 'dict_label': '进行中', 'sort_order': 2},
            {'dict_type': 'temporary_repair_status', 'dict_key': 'completed', 'dict_value': '已完成', 'dict_label': '已完成', 'sort_order': 3},
            {'dict_type': 'temporary_repair_status', 'dict_key': 'cancelled', 'dict_value': '已取消', 'dict_label': '已取消', 'sort_order': 4},
            
            # 零星用工单状态
            {'dict_type': 'spot_work_status', 'dict_key': 'not_started', 'dict_value': '未进行', 'dict_label': '未进行', 'sort_order': 1},
            {'dict_type': 'spot_work_status', 'dict_key': 'pending_confirm', 'dict_value': '待确认', 'dict_label': '待确认', 'sort_order': 2},
            {'dict_type': 'spot_work_status', 'dict_key': 'in_progress', 'dict_value': '进行中', 'dict_label': '进行中', 'sort_order': 3},
            {'dict_type': 'spot_work_status', 'dict_key': 'completed', 'dict_value': '已完成', 'dict_label': '已完成', 'sort_order': 4},
            
            # 定期巡检单状态
            {'dict_type': 'periodic_inspection_status', 'dict_key': 'not_started', 'dict_value': '未进行', 'dict_label': '未进行', 'sort_order': 1},
            {'dict_type': 'periodic_inspection_status', 'dict_key': 'pending_confirm', 'dict_value': '待确认', 'dict_label': '待确认', 'sort_order': 2},
            {'dict_type': 'periodic_inspection_status', 'dict_key': 'confirmed', 'dict_value': '已确认', 'dict_label': '已确认', 'sort_order': 3},
            {'dict_type': 'periodic_inspection_status', 'dict_key': 'in_progress', 'dict_value': '进行中', 'dict_label': '进行中', 'sort_order': 4},
            {'dict_type': 'periodic_inspection_status', 'dict_key': 'completed', 'dict_value': '已完成', 'dict_label': '已完成', 'sort_order': 5},
            {'dict_type': 'periodic_inspection_status', 'dict_key': 'cancelled', 'dict_value': '已取消', 'dict_label': '已取消', 'sort_order': 6},
            
            # 维保计划状态
            {'dict_type': 'maintenance_plan_status', 'dict_key': 'pending', 'dict_value': '待执行', 'dict_label': '待执行', 'sort_order': 1},
            {'dict_type': 'maintenance_plan_status', 'dict_key': 'in_progress', 'dict_value': '执行中', 'dict_label': '执行中', 'sort_order': 2},
            {'dict_type': 'maintenance_plan_status', 'dict_key': 'completed', 'dict_value': '已完成', 'dict_label': '已完成', 'sort_order': 3},
            {'dict_type': 'maintenance_plan_status', 'dict_key': 'cancelled', 'dict_value': '已取消', 'dict_label': '已取消', 'sort_order': 4},
            {'dict_type': 'maintenance_plan_status', 'dict_key': 'delayed', 'dict_value': '已延期', 'dict_label': '已延期', 'sort_order': 5},
            
            # 维保计划执行状态
            {'dict_type': 'maintenance_execution_status', 'dict_key': 'not_started', 'dict_value': '未开始', 'dict_label': '未开始', 'sort_order': 1},
            {'dict_type': 'maintenance_execution_status', 'dict_key': 'in_progress', 'dict_value': '进行中', 'dict_label': '进行中', 'sort_order': 2},
            {'dict_type': 'maintenance_execution_status', 'dict_key': 'completed', 'dict_value': '已完成', 'dict_label': '已完成', 'sort_order': 3},
            {'dict_type': 'maintenance_execution_status', 'dict_key': 'cancelled', 'dict_value': '已取消', 'dict_label': '已取消', 'sort_order': 4},
            {'dict_type': 'maintenance_execution_status', 'dict_key': 'abnormal', 'dict_value': '异常', 'dict_label': '异常', 'sort_order': 5},
            
            # 维保计划类型
            {'dict_type': 'maintenance_plan_type', 'dict_key': 'regular', 'dict_value': '定期维保', 'dict_label': '定期维保', 'sort_order': 1},
            {'dict_type': 'maintenance_plan_type', 'dict_key': 'preventive', 'dict_value': '预防性维保', 'dict_label': '预防性维保', 'sort_order': 2},
            {'dict_type': 'maintenance_plan_type', 'dict_key': 'fault_repair', 'dict_value': '故障维修', 'dict_label': '故障维修', 'sort_order': 3},
            {'dict_type': 'maintenance_plan_type', 'dict_key': 'inspection', 'dict_value': '巡检', 'dict_label': '巡检', 'sort_order': 4},
            {'dict_type': 'maintenance_plan_type', 'dict_key': 'other', 'dict_value': '其他', 'dict_label': '其他', 'sort_order': 5},
            
            # 备品备件状态
            {'dict_type': 'spare_parts_status', 'dict_key': 'normal', 'dict_value': '正常', 'dict_label': '正常', 'sort_order': 1},
            {'dict_type': 'spare_parts_status', 'dict_key': 'low_stock', 'dict_value': '库存不足', 'dict_label': '库存不足', 'sort_order': 2},
            {'dict_type': 'spare_parts_status', 'dict_key': 'out_of_stock', 'dict_value': '缺货', 'dict_label': '缺货', 'sort_order': 3},
            {'dict_type': 'spare_parts_status', 'dict_key': 'expired', 'dict_value': '已过期', 'dict_label': '已过期', 'sort_order': 4},
            {'dict_type': 'spare_parts_status', 'dict_key': 'near_expiry', 'dict_value': '即将过期', 'dict_label': '即将过期', 'sort_order': 5},
        ]
        
        for data in dictionary_data:
            existing = db.query(Dictionary).filter(
                Dictionary.dict_type == data['dict_type'],
                Dictionary.dict_key == data['dict_key']
            ).first()
            
            if not existing:
                dictionary = Dictionary(**data)
                db.add(dictionary)
                logger.info(f"添加字典: {data['dict_type']} - {data['dict_key']} - {data['dict_label']}")
            else:
                logger.info(f"字典已存在，跳过: {data['dict_type']} - {data['dict_key']}")
        
        db.commit()
        logger.info("字典数据初始化完成")
        
    except Exception as e:
        db.rollback()
        logger.error(f"初始化字典数据失败: {str(e)}", exc_info=True)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    init_dictionary_data()
