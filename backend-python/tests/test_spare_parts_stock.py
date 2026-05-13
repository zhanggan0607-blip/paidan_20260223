import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from app.services.spare_parts_stock import SparePartsStockService


class TestSparePartsStockServiceGenerateInboundNo:
    def test_generate_inbound_no_format(self):
        result = SparePartsStockService.generate_inbound_no()
        assert result.startswith("IN")
        assert len(result) > 10

    def test_generate_inbound_no_unique(self):
        results = set()
        for _ in range(100):
            results.add(SparePartsStockService.generate_inbound_no())
        assert len(results) == 100


class TestSparePartsStockServiceGetStock:
    @patch('app.services.spare_parts_stock.SparePartsStockRepository')
    @patch('app.services.spare_parts_stock.SparePartsInboundRepository')
    def test_get_stock_with_product_name(self, mock_inbound_class, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_item = Mock()
        mock_item.to_dict.return_value = {"product_name": "螺丝", "quantity": 100}
        mock_repo.search_stock.return_value = [mock_item]

        service = SparePartsStockService(mock_db)
        result = service.get_stock("螺丝")

        assert "items" in result
        assert result["total"] == 1
        mock_repo.search_stock.assert_called_once_with("螺丝")

    @patch('app.services.spare_parts_stock.SparePartsStockRepository')
    @patch('app.services.spare_parts_stock.SparePartsInboundRepository')
    def test_get_stock_all(self, mock_inbound_class, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_item1 = Mock()
        mock_item1.to_dict.return_value = {"product_name": "螺丝", "quantity": 100}
        mock_item2 = Mock()
        mock_item2.to_dict.return_value = {"product_name": "扳手", "quantity": 50}
        mock_repo.search_stock.return_value = [mock_item1, mock_item2]

        service = SparePartsStockService(mock_db)
        result = service.get_stock(None)

        assert result["total"] == 2


class TestSparePartsStockServiceGetProducts:
    @patch('app.services.spare_parts_stock.SparePartsStockRepository')
    @patch('app.services.spare_parts_stock.SparePartsInboundRepository')
    def test_get_products(self, mock_inbound_class, mock_repo_class):
        mock_db = Mock(spec=Session)
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_item = Mock()
        mock_item.id = 1
        mock_item.product_name = "螺丝"
        mock_item.brand = "品牌A"
        mock_item.model = "M10"
        mock_item.unit = "个"
        mock_repo.get_products.return_value = [mock_item]

        service = SparePartsStockService(mock_db)
        result = service.get_products(None)

        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["productName"] == "螺丝"
