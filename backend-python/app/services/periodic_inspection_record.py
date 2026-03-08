"""
巡检记录服务
提供巡检记录业务逻辑处理
"""
import json

from sqlalchemy.orm import Session

from app.models.periodic_inspection_record import PeriodicInspectionRecord
from app.repositories.periodic_inspection_record import PeriodicInspectionRecordRepository
from app.schemas.periodic_inspection_record import (
    BatchRecordSave,
    PeriodicInspectionRecordCreate,
    PeriodicInspectionRecordUpdate,
)


class PeriodicInspectionRecordService:
    """
    巡检记录服务
    提供巡检记录的增删改查等业务逻辑
    """

    def __init__(self, db: Session):
        self.repository = PeriodicInspectionRecordRepository(db)
        self._db = db

    def get_by_inspection_id(self, inspection_id: str) -> list[PeriodicInspectionRecord]:
        """
        根据巡检单编号获取所有记录

        Args:
            inspection_id: 巡检单编号

        Returns:
            巡检记录列表
        """
        return self.repository.find_by_inspection_id(inspection_id)

    def get_by_id(self, record_id: int) -> PeriodicInspectionRecord | None:
        """
        根据ID获取巡检记录

        Args:
            record_id: 记录ID

        Returns:
            巡检记录
        """
        return self.repository.find_by_id(record_id)

    def create(self, dto: PeriodicInspectionRecordCreate) -> PeriodicInspectionRecord:
        """
        创建巡检记录

        Args:
            dto: 创建数据传输对象

        Returns:
            创建的记录
        """
        result = self.upsert(dto)
        self._db.commit()
        return result

    def update(self, record_id: int, dto: PeriodicInspectionRecordUpdate) -> PeriodicInspectionRecord:
        """
        更新巡检记录

        Args:
            record_id: 记录ID
            dto: 更新数据传输对象

        Returns:
            更新后的记录
        """
        record = self.get_by_id(record_id)
        if not record:
            raise ValueError(f"记录不存在 (id={record_id})")

        if dto.inspected is not None:
            record.inspected = dto.inspected
        if dto.photos is not None:
            record.photos = json.dumps(dto.photos)
        if dto.inspection_result is not None:
            record.inspection_result = dto.inspection_result

        result = self.repository.update(record)
        self._db.commit()
        return result

    def upsert(self, dto: PeriodicInspectionRecordCreate) -> PeriodicInspectionRecord:
        """
        创建或更新巡检记录

        Args:
            dto: 创建数据传输对象

        Returns:
            创建或更新后的记录
        """
        return self.repository.upsert(
            inspection_id=dto.inspection_id,
            item_id=dto.item_id,
            item_name=dto.item_name,
            inspection_item=dto.inspection_item,
            inspection_content=dto.inspection_content,
            check_content=dto.check_content,
            brief_description=dto.brief_description,
            equipment_name=dto.equipment_name,
            equipment_location=dto.equipment_location,
            inspected=dto.inspected or False,
            photos=json.dumps(dto.photos) if dto.photos else '[]',
            inspection_result=dto.inspection_result
        )

    def batch_save(self, dto: BatchRecordSave) -> list[PeriodicInspectionRecord]:
        """
        批量保存巡检记录

        Args:
            dto: 批量保存数据传输对象

        Returns:
            保存的记录列表
        """
        results = []
        for record_dto in dto.records:
            record_dto.inspection_id = dto.inspection_id
            result = self.upsert(record_dto)
            results.append(result)
        self._db.commit()
        return results

    def delete(self, record_id: int) -> None:
        """
        删除巡检记录

        Args:
            record_id: 记录ID
        """
        record = self.get_by_id(record_id)
        if record:
            self.repository.delete(record)

    def delete_by_inspection_id(self, inspection_id: str) -> int:
        """
        删除指定巡检单的所有记录

        Args:
            inspection_id: 巡检单编号

        Returns:
            删除的记录数量
        """
        return self.repository.delete_by_inspection_id(inspection_id)
