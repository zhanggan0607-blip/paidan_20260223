# Java 到 Python 后端迁移文档

## 1. 迁移概述

本文档详细说明了将 SSTCP 工程维保管理系统后端从 Java (Spring Boot) 架构迁移到 Python (FastAPI) 架构的完整过程。

### 1.1 迁移目标

- 保持业务功能的完整性
- 确保数据的一致性
- 优化系统性能和可维护性
- 提供平滑的过渡体验
- 实现接口兼容性

### 1.2 技术栈对比

| 组件 | Java (Spring Boot) | Python (FastAPI) |
|------|-------------------|-------------------|
| Web 框架 | Spring Boot 3.2.0 | FastAPI 0.109.0 |
| ORM | Spring Data JPA | SQLAlchemy 2.0.25 |
| 数据库驱动 | MySQL Connector | PyMySQL |
| 数据验证 | Jakarta Validation | Pydantic 2.5.3 |
| API 文档 | SpringDoc OpenAPI | FastAPI 自动生成 |
| 异步处理 | Spring Async | asyncio + uvicorn |
| 依赖管理 | Maven | Poetry / pip |

## 2. 架构设计

### 2.1 分层架构

Python 版本保持了与 Java 版本相同的分层架构：

```
┌─────────────────────────────────────┐
│         API Layer (Routes)         │  ← 对应 Java Controller
├─────────────────────────────────────┤
│      Service Layer (Business)       │  ← 对应 Java Service
├─────────────────────────────────────┤
│    Repository Layer (Data Access)   │  ← 对应 Java Repository
├─────────────────────────────────────┤
│         Model Layer (ORM)          │  ← 对应 Java Entity
└─────────────────────────────────────┘
```

### 2.2 项目结构对比

#### Java 项目结构
```
backend/
├── src/main/java/com/sstcp/maintenancesystem/
│   ├── controller/          # 控制器层
│   ├── service/            # 业务逻辑层
│   ├── repository/         # 数据访问层
│   ├── entity/            # 实体模型
│   ├── dto/               # 数据传输对象
│   └── exception/         # 异常处理
└── src/main/resources/
    └── application.yml    # 配置文件
```

#### Python 项目结构
```
backend-python/
├── app/
│   ├── api/v1/           # API 路由层
│   ├── services/          # 业务逻辑层
│   ├── repositories/      # 数据访问层
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic 模型
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   └── main.py           # 应用入口
├── tests/                # 测试目录
└── requirements.txt       # 依赖管理
```

## 3. 核心组件迁移

### 3.1 数据模型迁移

#### Java Entity (JPA)
```java
@Entity
@Table(name = "project_info")
@Data
public class ProjectInfo {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(name = "project_id", nullable = false, unique = true)
    private String projectId;
    
    // ... 其他字段
}
```

#### Python Model (SQLAlchemy)
```python
from sqlalchemy import Column, BigInteger, String, DateTime
from app.database import Base

class ProjectInfo(Base):
    __tablename__ = "project_info"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    project_id = Column(String(50), nullable=False, unique=True)
    
    # ... 其他字段
```

### 3.2 数据传输对象 (DTO) 迁移

#### Java DTO
```java
public class ProjectInfoCreateDTO {
    @NotBlank
    private String projectId;
    
    @NotBlank
    private String projectName;
    
    // ... 其他字段
}
```

#### Python Schema (Pydantic)
```python
from pydantic import BaseModel, Field

class ProjectInfoCreate(BaseModel):
    project_id: str = Field(..., max_length=50)
    project_name: str = Field(..., max_length=200)
    
    # ... 其他字段
```

### 3.3 服务层迁移

#### Java Service
```java
@Service
@RequiredArgsConstructor
public class ProjectInfoService {
    private final ProjectInfoRepository repository;
    
    public ProjectInfo create(ProjectInfoCreateDTO dto) {
        // 业务逻辑
    }
}
```

#### Python Service
```python
class ProjectInfoService:
    def __init__(self, db: Session):
        self.repository = ProjectInfoRepository(db)
    
    def create(self, dto: ProjectInfoCreate) -> ProjectInfo:
        # 业务逻辑
```

### 3.4 控制器迁移

#### Java Controller
```java
@RestController
@RequestMapping("/api/project-info")
public class ProjectInfoController {
    private final ProjectInfoService service;
    
    @PostMapping
    public ApiResponse<ProjectInfo> create(@Valid @RequestBody ProjectInfoCreateDTO dto) {
        return ApiResponse.success(service.create(dto));
    }
}
```

#### Python Router
```python
router = APIRouter(prefix="/project-info")

@router.post("", response_model=ApiResponse)
def create_project_info(
    dto: ProjectInfoCreate,
    db: Session = Depends(get_db)
):
    service = ProjectInfoService(db)
    return ApiResponse.success(service.create(dto).to_dict())
```

## 4. 配置迁移

### 4.1 数据库配置

#### Java (application.yml)
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/sstcp_maintenance
    username: root
    password: root
    driver-class-name: com.mysql.cj.jdbc.Driver
```

#### Python (config.py)
```python
class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:root@localhost:3306/sstcp_maintenance"
```

### 4.2 API 配置

#### Java
```yaml
server:
  port: 8080
  servlet:
    context-path: /api

springdoc:
  api-docs:
    path: /v3/api-docs
  swagger-ui:
    path: /swagger-ui.html
```

#### Python
```python
app = FastAPI(
    title="SSTCP Maintenance System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
```

## 5. API 接口兼容性

### 5.1 响应格式

#### Java 响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

#### Python 响应格式
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 5.2 分页响应

#### Java 分页响应
```json
{
  "content": [...],
  "totalElements": 100,
  "totalPages": 10,
  "size": 10,
  "number": 0,
  "first": true,
  "last": false
}
```

#### Python 分页响应
```json
{
  "content": [...],
  "totalElements": 100,
  "totalPages": 10,
  "size": 10,
  "number": 0,
  "first": true,
  "last": false
}
```

## 6. 数据迁移策略

### 6.1 数据库迁移

由于两个版本使用相同的数据库结构和 MySQL 数据库，数据迁移不是必需的。只需确保：

1. 数据库表结构保持一致
2. 字段类型和约束相同
3. 索引配置一致

### 6.2 数据验证

使用以下步骤验证数据一致性：

```python
# 运行数据验证脚本
python scripts/validate_data.py
```

## 7. 测试策略

### 7.1 单元测试

#### Java (JUnit)
```java
@SpringBootTest
class ProjectInfoServiceTest {
    @Test
    void testCreateProjectInfo() {
        // 测试代码
    }
}
```

#### Python (pytest)
```python
def test_create_project_info(db):
    response = client.post("/api/project-info", json={...})
    assert response.status_code == 201
```

### 7.2 集成测试

使用 FastAPI 的 TestClient 进行集成测试：

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_integration():
    response = client.get("/api/project-info")
    assert response.status_code == 200
```

## 8. 部署策略

### 8.1 灰度发布

1. **阶段 1**: 部署 Python 版本到测试环境
2. **阶段 2**: 使用流量分流，10% 流量到 Python 版本
3. **阶段 3**: 逐步增加 Python 版本流量比例
4. **阶段 4**: 完全切换到 Python 版本

### 8.2 回滚方案

如果出现问题，可以快速回滚到 Java 版本：

1. 停止 Python 服务
2. 启动 Java 服务
3. 恢复数据库连接配置

## 9. 性能优化

### 9.1 数据库优化

- 使用连接池（SQLAlchemy 已内置）
- 添加适当的索引
- 优化查询语句
- 使用缓存

### 9.2 应用优化

- 异步处理 I/O 操作
- 使用 Gunicorn + Uvicorn Workers
- 启用响应压缩
- 配置适当的日志级别

## 10. 监控和日志

### 10.1 日志配置

#### Java
```yaml
logging:
  level:
    com.sstcp: DEBUG
    org.hibernate.SQL: DEBUG
```

#### Python
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 10.2 性能监控

- 使用 APM 工具（如 New Relic, Datadog）
- 监控响应时间
- 监控错误率
- 监控数据库查询性能

## 11. 安全性

### 11.1 CORS 配置

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 11.2 输入验证

使用 Pydantic 进行自动输入验证：

```python
class ProjectInfoCreate(BaseModel):
    project_id: str = Field(..., max_length=50)
    
    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v):
        if not v:
            raise ValueError('项目编号不能为空')
        return v
```

## 12. 故障排除

### 12.1 常见问题

#### 数据库连接失败
- 检查数据库连接字符串
- 确认数据库服务正在运行
- 验证用户名和密码

#### 端口冲突
- 修改启动端口
- 停止占用端口的进程

#### 依赖安装失败
- 使用虚拟环境
- 检查 Python 版本兼容性

## 13. 迁移检查清单

- [x] 分析现有 Java 代码结构
- [x] 设计 Python 技术栈
- [x] 创建 Python 项目结构
- [x] 实现数据模型
- [x] 实现 API 接口
- [x] 实现业务逻辑
- [x] 编写单元测试
- [x] 编写集成测试
- [x] 配置 CORS
- [x] 编写 API 文档
- [ ] 性能测试
- [ ] 部署到测试环境
- [ ] 灰度发布
- [ ] 监控和优化
- [ ] 完全切换

## 14. 后续优化建议

1. **异步数据库操作**: 使用 SQLAlchemy 的异步支持
2. **缓存层**: 添加 Redis 缓存
3. **消息队列**: 使用 Celery 处理异步任务
4. **API 网关**: 使用 Kong 或 Nginx 作为 API 网关
5. **容器化**: 使用 Docker 和 Kubernetes 部署
6. **CI/CD**: 配置自动化部署流程

## 15. 联系方式

如有迁移相关问题，请联系：
- 技术支持: tech-support@sstcp.com
- 项目负责人: project-manager@sstcp.com

---

**文档版本**: 1.0.0  
**最后更新**: 2025-01-26  
**维护者**: SSTCP 技术团队
