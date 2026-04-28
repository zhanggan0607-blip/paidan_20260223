"""
服务层测试
测试业务逻辑和数据处理
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.base import BaseService
from app.services.personnel import PersonnelService
from app.models.personnel import Personnel


class TestBaseService:
    """BaseService 基类测试"""

    def test_commit_success(self):
        """测试事务提交成功"""
        mock_db = Mock(spec=Session)
        service = BaseService(mock_db)
        service.commit()
        mock_db.commit.assert_called_once()

    def test_commit_failure_rollback(self):
        """测试事务提交失败后回滚"""
        mock_db = Mock(spec=Session)
        mock_db.commit.side_effect = Exception("Commit failed")
        service = BaseService(mock_db)
        
        with pytest.raises(Exception):
            service.commit()
        
        mock_db.rollback.assert_called_once()

    def test_rollback(self):
        """测试事务回滚"""
        mock_db = Mock(spec=Session)
        service = BaseService(mock_db)
        service.rollback()
        mock_db.rollback.assert_called_once()


class TestPersonnelService:
    """人员服务测试"""

    @patch('app.services.personnel.PersonnelRepository')
    def test_get_all_personnel(self, mock_repo_class):
        """测试获取所有人员"""
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_personnel = [
            Personnel(id=1, name="张三", role="管理员"),
            Personnel(id=2, name="李四", role="运维人员"),
        ]
        mock_repo.find_all.return_value = (mock_personnel, 2)

        service = PersonnelService(mock_db)
        result, total = service.get_all()

        assert total == 2
        assert result[0].name == "张三"

    @patch('app.services.personnel.PersonnelRepository')
    def test_create_personnel(self, mock_repo_class):
        """测试创建人员"""
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        new_personnel = Personnel(id=1, name="王五", gender="男", role="运维人员")
        mock_repo.create.return_value = new_personnel

        from app.schemas.personnel import PersonnelCreate
        dto = PersonnelCreate(name="王五", gender="男", role="运维人员")

        service = PersonnelService(mock_db)
        result = service.create(dto)

        assert result.name == "王五"
        mock_repo.create.assert_called_once()


class TestValidationService:
    """验证服务测试"""

    def test_validate_phone_number(self):
        """测试手机号验证"""
        valid_phones = ["13800138000", "15912345678", "18600001111"]
        invalid_phones = ["123", "123456789012345", "abc12345678"]
        
        for phone in valid_phones:
            assert len(phone) == 11
            assert phone.isdigit()
        
        for phone in invalid_phones:
            assert not (len(phone) == 11 and phone.isdigit())

    def test_validate_id_card(self):
        """测试身份证号验证"""
        valid_id = "110101199001011234"
        assert len(valid_id) == 18
        
        invalid_id = "123"
        assert len(invalid_id) != 18
