"""
测试工具函数
"""
import pytest
from datetime import datetime


class TestUtils:
    """
    工具函数测试类
    """

    def test_date_format(self):
        """
        测试日期格式
        """
        from app.utils.date_utils import format_date
        
        test_date = datetime(2024, 1, 15)
        result = format_date(test_date)
        assert result == "2024-01-15"

    def test_date_format_none(self):
        """
        测试空日期格式
        """
        from app.utils.date_utils import format_date
        
        result = format_date(None)
        assert result is None or result == ""
