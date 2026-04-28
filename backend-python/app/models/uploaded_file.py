"""
上传文件模型
支持OSS和数据库双存储模式，新文件优先存OSS，旧数据兼容从数据库读取
"""
import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, Index, LargeBinary, String, Text
from sqlalchemy.sql import func

from app.database import Base


class UploadedFile(Base):
    """
    上传文件表
    支持两种存储模式：
    - oss: 文件存储在阿里云OSS，file_data为空，oss_url记录访问地址
    - database: 文件以二进制形式存储在数据库中（兼容旧数据）
    """
    __tablename__ = "uploaded_file"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    file_id = Column(String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), comment="文件唯一标识UUID")
    original_filename = Column(String(255), comment="原始文件名")
    stored_filename = Column(String(255), nullable=False, comment="存储文件名")
    content_type = Column(String(100), comment="文件MIME类型")
    file_data = Column(LargeBinary, nullable=True, comment="文件二进制数据（仅database模式）")
    file_size = Column(BigInteger, nullable=False, comment="文件大小(字节)")
    file_path = Column(String(500), comment="文件路径(用于兼容旧数据)")
    upload_date = Column(String(10), nullable=False, comment="上传日期(YYYYMMDD)")
    storage_type = Column(String(20), default="database", comment="存储类型: oss/database")
    oss_url = Column(String(1000), nullable=True, comment="OSS访问URL")
    created_at = Column(DateTime, server_default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    __table_args__ = (
        Index('idx_uploaded_file_id', 'file_id'),
        Index('idx_uploaded_file_path', 'file_path'),
        Index('idx_uploaded_upload_date', 'upload_date'),
        Index('idx_uploaded_storage_type', 'storage_type'),
        {'comment': '上传文件表'}
    )

    def to_dict(self):
        """
        转换为字典
        """
        return {
            'id': self.id,
            'file_id': self.file_id,
            'original_filename': self.original_filename,
            'stored_filename': self.stored_filename,
            'content_type': self.content_type,
            'file_size': self.file_size,
            'file_path': self.file_path,
            'upload_date': self.upload_date,
            'storage_type': self.storage_type,
            'oss_url': self.oss_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def generate_file_path(upload_date: str, filename: str) -> str:
        """
        生成文件路径

        Args:
            upload_date: 上传日期(YYYYMMDD)
            filename: 文件名

        Returns:
            文件路径，格式: /uploads/YYYYMMDD/filename
        """
        return f"/uploads/{upload_date}/{filename}"
