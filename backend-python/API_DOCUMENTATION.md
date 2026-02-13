# SSTCP Maintenance System API Documentation

## Base URL

```
http://localhost:8080/api
```

## Authentication

当前版本不需要身份验证。

## Common Response Format

所有 API 响应遵循以下格式：

### Success Response
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### Error Response
```json
{
  "code": 400,
  "message": "Error message",
  "data": null
}
```

### Validation Error Response
```json
{
  "code": 422,
  "message": "参数验证失败",
  "data": {
    "errors": [
      {
        "field": "field_name",
        "message": "Error message",
        "type": "value_error"
      }
    ]
  }
}
```

## Project Info API

### Get Project Info List

获取项目信息列表，支持分页和条件查询。

**Endpoint:** `GET /project-info`

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|----------|-------------|
| page | integer | No | 0 | 页码，从0开始 |
| size | integer | No | 10 | 每页大小 (1-100) |
| project_name | string | No | - | 项目名称（模糊查询） |
| client_name | string | No | - | 客户名称（模糊查询） |

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "content": [
      {
        "id": 1,
        "project_id": "PRJ-2025-001",
        "project_name": "上海中心大厦维保项目",
        "completion_date": "2024-12-31T00:00:00",
        "maintenance_end_date": "2026-12-31T00:00:00",
        "maintenance_period": "每半年",
        "client_name": "上海城投（集团）有限公司",
        "address": "上海市浦东新区陆家嘴银城中路501号",
        "project_abbr": "SHZX",
        "client_contact": "张三",
        "client_contact_position": "经理",
        "client_contact_info": "13800138000",
        "created_at": "2024-01-26T10:00:00",
        "updated_at": "2024-01-26T10:00:00"
      }
    ],
    "totalElements": 100,
    "totalPages": 10,
    "size": 10,
    "number": 0,
    "first": true,
    "last": false
  }
}
```

**Example:**
```bash
curl -X GET "http://localhost:8080/api/project-info?page=0&size=10&project_name=上海"
```

### Get Project Info by ID

根据项目ID获取详细信息。

**Endpoint:** `GET /project-info/{id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | 项目ID |

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "project_id": "PRJ-2025-001",
    "project_name": "上海中心大厦维保项目",
    "completion_date": "2024-12-31T00:00:00",
    "maintenance_end_date": "2026-12-31T00:00:00",
    "maintenance_period": "每半年",
    "client_name": "上海城投（集团）有限公司",
    "address": "上海市浦东新区陆家嘴银城中路501号",
    "project_abbr": "SHZX",
    "client_contact": "张三",
    "client_contact_position": "经理",
    "client_contact_info": "13800138000",
    "created_at": "2024-01-26T10:00:00",
    "updated_at": "2024-01-26T10:00:00"
  }
}
```

**Example:**
```bash
curl -X GET "http://localhost:8080/api/project-info/1"
```

### Create Project Info

创建新的项目信息。

**Endpoint:** `POST /project-info`

**Request Body:**
```json
{
  "project_id": "PRJ-2025-002",
  "project_name": "新项目名称",
  "completion_date": "2024-01-01T00:00:00",
  "maintenance_end_date": "2025-12-31T00:00:00",
  "maintenance_period": "每月",
  "client_unit": "客户单位名称",
  "client_address": "客户地址",
  "project_abbr": "项目简称（可选）",
  "client_contact": "客户联系人（可选）",
  "client_contact_position": "客户联系人职位（可选）",
  "client_contact_info": "客户联系方式（可选）"
}
```

**Request Body Fields:**

| Field | Type | Required | Max Length | Description |
|-------|------|----------|-------------|-------------|
| project_id | string | Yes | 50 | 项目编号，必须唯一 |
| project_name | string | Yes | 200 | 项目名称 |
| completion_date | datetime | Yes | - | 开始日期（ISO 8601格式） |
| maintenance_end_date | datetime | Yes | - | 结束日期（ISO 8601格式） |
| maintenance_period | string | Yes | 20 | 维保频率（每天/每周/每月/每季度/每半年） |
| client_unit | string | Yes | 100 | 客户单位名称 |
| client_address | string | Yes | 200 | 客户地址 |
| project_abbr | string | No | 10 | 项目简称 |
| client_contact | string | No | 50 | 客户联系人 |
| client_contact_position | string | No | 20 | 客户联系人职位 |
| client_contact_info | string | No | 50 | 客户联系方式 |

**Response:**
```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 2,
    "project_id": "PRJ-2025-002",
    "project_name": "新项目名称",
    "completion_date": "2024-01-01T00:00:00",
    "maintenance_end_date": "2025-12-31T00:00:00",
    "maintenance_period": "每月",
    "client_name": "客户单位名称",
    "address": "客户地址",
    "project_abbr": "项目简称",
    "client_contact": "客户联系人",
    "client_contact_position": "客户联系人职位",
    "client_contact_info": "客户联系方式",
    "created_at": "2024-01-26T10:00:00",
    "updated_at": "2024-01-26T10:00:00"
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8080/api/project-info" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "PRJ-2025-002",
    "project_name": "新项目名称",
    "completion_date": "2024-01-01T00:00:00",
    "maintenance_end_date": "2025-12-31T00:00:00",
    "maintenance_period": "每月",
    "client_unit": "客户单位名称",
    "client_address": "客户地址"
  }'
```

### Update Project Info

根据ID更新项目信息。

**Endpoint:** `PUT /project-info/{id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | 项目ID |

**Request Body:**
```json
{
  "project_id": "PRJ-2025-002",
  "project_name": "更新后的项目名称",
  "completion_date": "2024-01-01T00:00:00",
  "maintenance_end_date": "2025-12-31T00:00:00",
  "maintenance_period": "每月",
  "client_name": "更新后的客户单位名称",
  "address": "更新后的客户地址",
  "project_abbr": "更新后的项目简称",
  "client_contact": "更新后的客户联系人",
  "client_contact_position": "更新后的客户联系人职位",
  "client_contact_info": "更新后的客户联系方式"
}
```

**Request Body Fields:**

| Field | Type | Required | Max Length | Description |
|-------|------|----------|-------------|-------------|
| project_id | string | Yes | 50 | 项目编号，必须唯一 |
| project_name | string | Yes | 200 | 项目名称 |
| completion_date | datetime | Yes | - | 开始日期（ISO 8601格式） |
| maintenance_end_date | datetime | Yes | - | 结束日期（ISO 8601格式） |
| maintenance_period | string | Yes | 20 | 维保频率（每天/每周/每月/每季度/每半年） |
| client_name | string | Yes | 100 | 客户单位名称 |
| address | string | Yes | 200 | 客户地址 |
| project_abbr | string | No | 10 | 项目简称 |
| client_contact | string | No | 50 | 客户联系人 |
| client_contact_position | string | No | 20 | 客户联系人职位 |
| client_contact_info | string | No | 50 | 客户联系方式 |

**Response:**
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 2,
    "project_id": "PRJ-2025-002",
    "project_name": "更新后的项目名称",
    "completion_date": "2024-01-01T00:00:00",
    "maintenance_end_date": "2025-12-31T00:00:00",
    "maintenance_period": "每月",
    "client_name": "更新后的客户单位名称",
    "address": "更新后的客户地址",
    "project_abbr": "更新后的项目简称",
    "client_contact": "更新后的客户联系人",
    "client_contact_position": "更新后的客户联系人职位",
    "client_contact_info": "更新后的客户联系方式",
    "created_at": "2024-01-26T10:00:00",
    "updated_at": "2024-01-26T10:00:00"
  }
}
```

**Example:**
```bash
curl -X PUT "http://localhost:8080/api/project-info/2" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "PRJ-2025-002",
    "project_name": "更新后的项目名称",
    "completion_date": "2024-01-01T00:00:00",
    "maintenance_end_date": "2025-12-31T00:00:00",
    "maintenance_period": "每月",
    "client_name": "更新后的客户单位名称",
    "address": "更新后的客户地址"
  }'
```

### Delete Project Info

根据ID删除项目信息。

**Endpoint:** `DELETE /project-info/{id}`

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| id | integer | Yes | 项目ID |

**Response:**
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

**Example:**
```bash
curl -X DELETE "http://localhost:8080/api/project-info/2"
```

### Get All Project Info

获取所有项目信息列表，不分页。

**Endpoint:** `GET /project-info/all/list`

**Response:**
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "project_id": "PRJ-2025-001",
      "project_name": "上海中心大厦维保项目",
      "completion_date": "2024-12-31T00:00:00",
      "maintenance_end_date": "2026-12-31T00:00:00",
      "maintenance_period": "每半年",
      "client_name": "上海城投（集团）有限公司",
      "address": "上海市浦东新区陆家嘴银城中路501号",
      "project_abbr": "SHZX",
      "client_contact": "张三",
      "client_contact_position": "经理",
      "client_contact_info": "13800138000",
      "created_at": "2024-01-26T10:00:00",
      "updated_at": "2024-01-26T10:00:00"
    }
  ]
}
```

**Example:**
```bash
curl -X GET "http://localhost:8080/api/project-info/all/list"
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

## Common Errors

### Project ID Already Exists
```json
{
  "code": 400,
  "message": "项目编号已存在",
  "data": null
}
```

### Project Not Found
```json
{
  "code": 404,
  "message": "项目信息不存在",
  "data": null
}
```

### Invalid Maintenance Period
```json
{
  "code": 422,
  "message": "参数验证失败",
  "data": {
    "errors": [
      {
        "field": "maintenance_period",
        "message": "维保频率必须是以下之一: 每天, 每周, 每月, 每季度, 每半年",
        "type": "value_error"
      }
    ]
  }
}
```

## Interactive API Documentation

访问以下地址查看交互式 API 文档：

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc
- **OpenAPI JSON**: http://localhost:8080/openapi.json

## Rate Limiting

当前版本未实施速率限制。

## Versioning

当前 API 版本: v1.0.0

API 版本通过 URL 路径管理: `/api/v1/...`

## Support

如有问题或建议，请联系技术支持团队。

---

**文档版本**: 1.0.0  
**最后更新**: 2025-01-26  
**维护者**: SSTCP 技术团队
