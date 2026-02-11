# 数据库迁移指南

本文档介绍如何使用 Alembic 进行数据库迁移。

## 安装 Alembic

```bash
pip install alembic
```

## 初始化 Alembic

如果还没有初始化 Alembic，运行以下命令：

```bash
alembic init alembic
```

## 创建迁移

当修改了数据库模型后，创建新的迁移：

```bash
alembic revision --autogenerate -m "描述迁移内容"
```

例如：

```bash
alembic revision --autogenerate -m "添加外键约束"
```

## 应用迁移

应用所有未应用的迁移：

```bash
alembic upgrade head
```

应用到特定版本：

```bash
alembic upgrade <revision_id>
```

## 回滚迁移

回滚到上一个版本：

```bash
alembic downgrade -1
```

回滚到特定版本：

```bash
alembic downgrade <revision_id>
```

## 查看迁移历史

查看所有迁移版本：

```bash
alembic history
```

查看当前版本：

```bash
alembic current
```

## 迁移文件位置

迁移文件位于 `alembic/versions/` 目录下。

## 注意事项

1. **备份数据库**：在生产环境应用迁移前，务必备份数据库
2. **测试迁移**：先在测试环境验证迁移脚本
3. **检查迁移**：应用迁移后，检查数据库结构是否正确
4. **版本控制**：将迁移文件提交到版本控制系统

## 常见迁移场景

### 添加新字段

```python
# 在模型中添加新字段
new_field = Column(String(100), nullable=True)

# 创建迁移
alembic revision --autogenerate -m "添加新字段"

# 应用迁移
alembic upgrade head
```

### 添加外键约束

```python
# 在模型中添加外键
project_id = Column(String(50), ForeignKey('project_info.project_id'), nullable=False)

# 创建迁移
alembic revision --autogenerate -m "添加外键约束"

# 应用迁移
alembic upgrade head
```

### 删除字段

```python
# 从模型中删除字段

# 创建迁移
alembic revision --autogenerate -m "删除字段"

# 应用迁移
alembic upgrade head
```

## 故障排除

### 迁移失败

如果迁移失败，检查以下几点：

1. 数据库连接是否正常
2. 迁移脚本是否有语法错误
3. 数据库中是否有数据冲突

### 手动修复

如果自动生成的迁移不正确，可以手动编辑迁移文件：

```python
# 编辑 alembic/versions/xxx_migration.py

def upgrade():
    # 手动编写升级逻辑
    pass

def downgrade():
    # 手动编写回滚逻辑
    pass
```

## 参考资料

- [Alembic 官方文档](https://alembic.sqlalchemy.org/)
- [SQLAlchemy 文档](https://docs.sqlalchemy.org/)