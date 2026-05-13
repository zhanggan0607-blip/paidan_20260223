import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.online_user import OnlineUserService


class TestOnlineUserServiceRecordLogin:
    @patch('app.services.online_user.OnlineUserRepository')
    def test_record_login_success(self, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        service = OnlineUserService(mock_db)
        result = service.record_login(1, "测试用户", "192.168.1.1", "pc")

        assert result["code"] == 200
        mock_repo.upsert_online_user.assert_called_once_with(1, "测试用户", "192.168.1.1", "pc")
        mock_db.commit.assert_called_once()


class TestOnlineUserServiceRecordLogout:
    @patch('app.services.online_user.OnlineUserRepository')
    def test_record_logout_success(self, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        service = OnlineUserService(mock_db)
        result = service.record_logout(1)

        assert result["code"] == 200
        mock_repo.set_user_offline.assert_called_once_with(1)


class TestOnlineUserServiceGetOnlineCount:
    @patch('app.services.online_user.OnlineUserRepository')
    def test_get_online_count(self, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.count_online.return_value = 5

        service = OnlineUserService(mock_db)
        result = service.get_online_count()

        assert result["code"] == 200
        assert result["data"]["count"] == 5


class TestOnlineUserServiceGetOnlineUsers:
    @patch('app.services.online_user.OnlineUserRepository')
    def test_get_online_users(self, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_user = Mock()
        mock_user.to_dict.return_value = {"user_id": 1, "user_name": "在线用户"}
        mock_repo.get_online_users.return_value = [mock_user]

        service = OnlineUserService(mock_db)
        result = service.get_online_users()

        assert result["code"] == 200
        assert len(result["data"]) == 1


class TestOnlineUserServiceGetOnlineStatusMap:
    @patch('app.services.online_user.OnlineUserRepository')
    def test_get_online_status_map(self, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_online_user = MagicMock()
        mock_online_user.user_id = 1
        mock_online_user.to_dict.return_value = {"user_id": 1, "is_online": True}
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_online_user]

        service = OnlineUserService(mock_db)
        result = service.get_online_status_map([1, 2])

        assert 1 in result
