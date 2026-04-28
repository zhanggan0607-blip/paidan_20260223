"""
阿里云OSS存储服务
提供文件上传、下载、删除等功能
新文件上传到OSS，旧数据兼容从数据库读取
"""
import logging
from datetime import datetime, timedelta
from typing import Optional

from app.config import get_settings
from app.utils.logging_config import get_logger

logger = get_logger(__name__)

_oss_service: Optional['OSSService'] = None


class OSSService:
    """
    阿里云OSS存储服务类

    新上传的文件存储到OSS，数据库仅保存元数据和路径引用
    旧数据兼容从数据库读取
    """

    def __init__(self):
        settings = get_settings()
        self._enabled = settings.aliyun_oss_enabled
        self._access_key_id = settings.aliyun_oss_access_key_id
        self._access_key_secret = settings.aliyun_oss_access_key_secret
        self._endpoint = settings.aliyun_oss_endpoint
        self._bucket_name = settings.aliyun_oss_bucket_name
        self._cdn_domain = settings.aliyun_oss_cdn_domain
        self._bucket = None

        if not self._enabled:
            logger.info("OSS存储已禁用，将使用数据库存储")
            return

        if not self._access_key_id or not self._access_key_secret:
            logger.warning("阿里云OSS配置未设置，请检查ALIYUN_OSS_ACCESS_KEY_ID和ALIYUN_OSS_ACCESS_KEY_SECRET")
            self._enabled = False
            return

        try:
            import oss2
            auth = oss2.Auth(self._access_key_id, self._access_key_secret)
            self._bucket = oss2.Bucket(auth, self._endpoint, self._bucket_name)
            self._bucket.get_bucket_info()
            logger.info(f"阿里云OSS连接成功: bucket={self._bucket_name}, endpoint={self._endpoint}")
        except Exception as e:
            logger.error(f"阿里云OSS连接失败: {str(e)}")
            self._enabled = False

    @property
    def is_available(self) -> bool:
        return self._enabled and self._bucket is not None

    def upload_file(
        self,
        file_data: bytes,
        oss_key: str,
        content_type: str = "image/jpeg",
    ) -> str:
        """
        上传文件到OSS

        Args:
            file_data: 文件二进制数据
            oss_key: OSS对象键（如 uploads/20260408/abc.jpg）
            content_type: 文件MIME类型

        Returns:
            str: 文件的OSS访问URL

        Raises:
            Exception: 上传失败时抛出异常
        """
        if not self.is_available:
            raise RuntimeError("OSS服务不可用")

        try:
            import oss2

            headers = {'Content-Type': content_type}
            self._bucket.put_object(oss_key, file_data, headers=headers)

            url = self.get_file_url(oss_key)
            logger.info(f"文件上传到OSS成功: {oss_key}")
            return url
        except Exception as e:
            logger.error(f"文件上传到OSS失败: {str(e)}")
            raise

    def get_file_url(self, oss_key: str) -> str:
        """
        获取文件的访问URL

        优先使用CDN域名，否则使用OSS默认域名

        Args:
            oss_key: OSS对象键

        Returns:
            str: 文件访问URL
        """
        if self._cdn_domain:
            return f"https://{self._cdn_domain}/{oss_key}"
        return f"https://{self._bucket_name}.{self._endpoint}/{oss_key}"

    def generate_signed_url(self, oss_key: str, expires: int = 3600) -> str:
        """
        生成带签名的临时访问URL

        Args:
            oss_key: OSS对象键
            expires: URL有效期（秒），默认1小时

        Returns:
            str: 带签名的访问URL
        """
        if not self.is_available:
            raise RuntimeError("OSS服务不可用")

        return self._bucket.sign_url('GET', oss_key, expires)

    def delete_file(self, oss_key: str) -> bool:
        """
        从OSS删除文件

        Args:
            oss_key: OSS对象键

        Returns:
            bool: 是否删除成功
        """
        if not self.is_available:
            return False

        try:
            self._bucket.delete_object(oss_key)
            logger.info(f"从OSS删除文件成功: {oss_key}")
            return True
        except Exception as e:
            logger.error(f"从OSS删除文件失败: {str(e)}")
            return False

    def file_exists(self, oss_key: str) -> bool:
        """
        检查文件是否存在于OSS

        Args:
            oss_key: OSS对象键

        Returns:
            bool: 是否存在
        """
        if not self.is_available:
            return False

        try:
            import oss2
            return self._bucket.object_exists(oss_key)
        except Exception as e:
            logger.error(f"检查OSS文件存在失败: {str(e)}")
            return False

    @staticmethod
    def generate_oss_key(upload_date: str, filename: str) -> str:
        """
        生成OSS对象键

        Args:
            upload_date: 上传日期（YYYYMMDD）
            filename: 文件名

        Returns:
            str: OSS对象键，如 uploads/20260408/abc.jpg
        """
        return f"uploads/{upload_date}/{filename}"


def get_oss_service() -> OSSService:
    """
    获取OSS服务实例（单例模式）

    Returns:
        OSSService: OSS服务实例
    """
    global _oss_service
    if _oss_service is None:
        _oss_service = OSSService()
    return _oss_service
