import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from app.services.spot_work import SpotWorkService
from app.exceptions import ValidationException


class TestSpotWorkServiceMaskIdCard:
    def test_normal_id_card(self):
        result = SpotWorkService._mask_id_card("110101199001011234")
        assert result == "110****1234"

    def test_short_id_card(self):
        result = SpotWorkService._mask_id_card("123456")
        assert result == "***"

    def test_empty_id_card(self):
        result = SpotWorkService._mask_id_card("")
        assert result == "***"

    def test_none_id_card(self):
        result = SpotWorkService._mask_id_card(None)
        assert result == "***"

    def test_exact_7_chars(self):
        result = SpotWorkService._mask_id_card("1234567")
        assert result == "123****4567"


class TestSpotWorkServiceDeleteWorker:
    @patch('app.services.spot_work.SpotWorkRepository')
    @patch('app.services.spot_work.SyncService')
    def test_delete_unlinked_worker(self, mock_sync_class, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        worker = MagicMock()
        worker.spot_work_id = None
        mock_repo.db.query.return_value.filter.return_value.first.return_value = worker
        mock_repo.delete_worker.return_value = True

        service = SpotWorkService(mock_db)
        result = service.delete_worker(1)

        assert result is True

    @patch('app.services.spot_work.SpotWorkRepository')
    @patch('app.services.spot_work.SyncService')
    def test_delete_linked_worker_raises(self, mock_sync_class, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        worker = MagicMock()
        worker.spot_work_id = 999
        mock_repo.db.query.return_value.filter.return_value.first.return_value = worker

        service = SpotWorkService(mock_db)
        with pytest.raises(ValidationException, match="已关联工单"):
            service.delete_worker(1)

    @patch('app.services.spot_work.SpotWorkRepository')
    @patch('app.services.spot_work.SyncService')
    def test_delete_nonexistent_worker(self, mock_sync_class, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        mock_repo.db.query.return_value.filter.return_value.first.return_value = None

        service = SpotWorkService(mock_db)
        result = service.delete_worker(999)

        assert result is False
