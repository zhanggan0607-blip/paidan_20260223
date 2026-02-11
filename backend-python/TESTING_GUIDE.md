# 单元测试指南

本文档介绍如何运行项目的单元测试。

## 安装测试依赖

```bash
pip install pytest pytest-asyncio httpx
```

## 运行测试

运行所有测试：

```bash
pytest
```

运行特定测试文件：

```bash
pytest tests/test_api.py
```

运行特定测试函数：

```bash
pytest tests/test_api.py::test_health_check
```

显示详细输出：

```bash
pytest -v
```

显示测试覆盖率：

```bash
pytest --cov=app --cov-report=html
```

## 测试文件位置

测试文件位于 `tests/` 目录下。

## 测试结构

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_personnel():
    response = client.post(
        "/api/v1/personnel",
        json={
            "name": "张三",
            "gender": "男",
            "phone": "13800138000",
            "department": "技术部",
            "role": "管理员"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == 200
    assert data["data"]["name"] == "张三"
```

## 测试最佳实践

1. **隔离性**：每个测试应该是独立的，不依赖其他测试
2. **可重复性**：测试应该可以重复运行，结果一致
3. **快速**：测试应该快速运行
4. **清晰**：测试名称应该清楚地描述测试的内容
5. **覆盖**：测试应该覆盖主要的业务逻辑

## 测试覆盖率

目标测试覆盖率：80% 以上

查看覆盖率报告：

```bash
pytest --cov=app --cov-report=html
```

报告将生成在 `htmlcov/` 目录下。

## 持续集成

在 CI/CD 流程中运行测试：

```yaml
- name: Run tests
  run: |
    pip install pytest pytest-asyncio httpx
    pytest --cov=app --cov-report=xml
```

## 故障排除

### 测试失败

如果测试失败，检查以下几点：

1. 数据库连接是否正常
2. 测试数据是否正确
3. API 端点是否正常工作
4. 测试断言是否正确

### 数据库问题

如果测试数据库有问题，删除测试数据库：

```bash
rm test.db
```

## 参考资料

- [Pytest 文档](https://docs.pytest.org/)
- [FastAPI 测试文档](https://fastapi.tiangolo.com/tutorial/testing/)