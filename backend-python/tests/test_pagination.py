import pytest
from app.schemas.common import PaginatedResponse, ApiResponse


class TestApiResponse:
    def test_success_with_data(self):
        response = ApiResponse.success(data={"key": "value"}, message="操作成功")
        assert response.code == 200
        assert response.message == "操作成功"
        assert response.data == {"key": "value"}

    def test_success_without_data(self):
        response = ApiResponse.success()
        assert response.code == 200
        assert response.message == "success"
        assert response.data is None

    def test_error_default(self):
        response = ApiResponse.error(message="操作失败")
        assert response.code == 500
        assert response.message == "操作失败"

    def test_error_custom_code(self):
        response = ApiResponse.error(message="未找到", code=404)
        assert response.code == 404
        assert response.message == "未找到"


class TestPaginatedResponse:
    def test_success_basic(self):
        items = [{"id": 1}, {"id": 2}]
        response = PaginatedResponse.success(items=items, total=10, page=0, size=2)
        assert response.code == 200
        assert response.data["total"] == 10
        assert response.data["totalElements"] == 10
        assert len(response.data["items"]) == 2
        assert len(response.data["content"]) == 2

    def test_success_pagination_fields(self):
        response = PaginatedResponse.success(items=[], total=25, page=1, size=10)
        assert response.data["page"] == 1
        assert response.data["number"] == 1
        assert response.data["size"] == 10
        assert response.data["totalPages"] == 3

    def test_success_first_page(self):
        response = PaginatedResponse.success(items=[], total=10, page=0, size=5)
        assert response.data["first"] is True
        assert response.data["last"] is False

    def test_success_last_page(self):
        response = PaginatedResponse.success(items=[], total=10, page=1, size=5)
        assert response.data["first"] is False
        assert response.data["last"] is True

    def test_success_single_page(self):
        response = PaginatedResponse.success(items=[], total=3, page=0, size=10)
        assert response.data["first"] is True
        assert response.data["last"] is True
        assert response.data["totalPages"] == 1

    def test_success_empty_result(self):
        response = PaginatedResponse.success(items=[], total=0, page=0, size=10)
        assert response.data["total"] == 0
        assert response.data["totalPages"] == 0
        assert response.data["items"] == []

    def test_success_total_pages_calculation(self):
        response = PaginatedResponse.success(items=[], total=11, page=0, size=5)
        assert response.data["totalPages"] == 3

    def test_success_exact_pages(self):
        response = PaginatedResponse.success(items=[], total=10, page=0, size=5)
        assert response.data["totalPages"] == 2
