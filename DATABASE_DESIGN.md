# 数据库设计文档

## 一、概述

本文档描述维保工单管理系统的数据库表结构、业务逻辑和表间关系。系统以项目信息为核心，围绕维保计划、工单管理、备品备件、维修工具等业务模块进行设计。

---

## 二、核心业务表（以项目为中心）

### 2.1 project_info（项目信息表）- 核心主表

**表名**: `project_info`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| project_id | String(50) | 是 | - | 项目编号（唯一） |
| project_name | String(200) | 是 | - | 项目名称 |
| completion_date | DateTime | 是 | - | 开始日期 |
| maintenance_end_date | DateTime | 是 | - | 结束日期 |
| maintenance_period | String(20) | 是 | - | 维保频率 |
| client_name | String(100) | 是 | - | 客户单位名称 |
| address | String(200) | 是 | - | 客户地址 |
| project_abbr | String(10) | 否 | - | 项目简称 |
| project_manager | String(50) | 否 | - | 项目负责人 |
| client_contact | String(50) | 否 | - | 客户联系人 |
| client_contact_position | String(20) | 否 | - | 客户联系人职位 |
| client_contact_info | String(50) | 否 | - | 客户联系方式 |
| created_at | DateTime | 否 | - | 创建时间 |
| updated_at | DateTime | 否 | - | 更新时间 |

**索引**:
- `idx_project_info_id`: project_id
- `idx_project_info_client_name`: client_name
- `idx_project_info_project_name`: project_name

**业务逻辑**:
- 所有业务数据的核心来源
- 其他业务表通过 `project_id` 关联
- 项目编号用于生成工单编号前缀
- 所有数据以 project_info 表数据为准

**关联关系**:
- 一对多 → temporary_repairs（临时维修单）
- 一对多 → spot_works（零星用工单）
- 一对多 → maintenance_plans（维保计划）
- 一对多 → periodic_inspections（定期巡检单）
- 一对多 → work_plans（工作计划）

---

### 2.2 maintenance_plan（维保计划表）

**表名**: `maintenance_plan`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| plan_id | String(50) | 是 | - | 计划编号（唯一） |
| plan_name | String(200) | 是 | - | 计划名称 |
| project_id | String(50) | 是 | - | 关联项目编号（外键） |
| project_name | String(200) | 否 | - | 项目名称 |
| plan_type | String(20) | 是 | - | 工单类型 |
| equipment_id | String(50) | 是 | - | 设备编号 |
| equipment_name | String(200) | 是 | - | 设备名称 |
| equipment_model | String(100) | 否 | - | 设备型号 |
| equipment_location | String(200) | 否 | - | 设备位置 |
| plan_start_date | DateTime | 是 | - | 计划开始日期 |
| plan_end_date | DateTime | 是 | - | 计划结束日期 |
| execution_date | DateTime | 否 | - | 执行日期 |
| next_maintenance_date | DateTime | 否 | - | 下次维保日期 |
| responsible_person | String(50) | 是 | - | 负责人 |
| responsible_department | String(100) | 否 | - | 负责部门 |
| contact_info | String(50) | 否 | - | 联系方式 |
| maintenance_content | Text | 是 | - | 维保内容 |
| maintenance_requirements | Text | 否 | - | 维保要求 |
| maintenance_standard | Text | 否 | - | 维保标准 |
| plan_status | String(20) | 是 | - | 计划状态 |
| execution_status | String(20) | 是 | - | 执行状态 |
| completion_rate | Integer | 否 | 0 | 完成率 |
| remarks | Text | 否 | - | 备注 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_maintenance_plan_id`: plan_id
- `idx_maintenance_project_id`: project_id
- `idx_maintenance_equipment_id`: equipment_id
- `idx_maintenance_plan_status`: plan_status
- `idx_maintenance_execution_status`: execution_status
- `idx_maintenance_execution_date`: execution_date

**业务逻辑**:
- 由管理员或部门经理制定
- 关联项目和设备信息
- 可生成工单（定期巡检/临时维修/零星用工）

---

### 2.3 work_plan（工作计划表）- 统一工单管理

**表名**: `work_plan`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| plan_id | String(50) | 是 | - | 计划编号（唯一） |
| plan_type | String(20) | 是 | - | 工单类型：定期巡检/临时维修/零星用工 |
| project_id | String(50) | 是 | - | 项目编号（外键） |
| project_name | String(200) | 是 | - | 项目名称 |
| plan_start_date | DateTime | 是 | - | 计划开始日期 |
| plan_end_date | DateTime | 是 | - | 计划结束日期 |
| client_name | String(100) | 否 | - | 客户单位 |
| maintenance_personnel | String(100) | 否 | - | 运维人员 |
| status | String(20) | 是 | 未进行 | 状态 |
| filled_count | Integer | 否 | 0 | 已填写检查项数量 |
| remarks | Text | 否 | - | 备注 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_work_plan_id`: plan_id
- `idx_work_plan_type`: plan_type
- `idx_work_plan_project_id`: project_id
- `idx_work_plan_project_name`: project_name
- `idx_work_plan_client_name`: client_name
- `idx_work_plan_status`: status
- `idx_work_plan_start_date`: plan_start_date

**业务逻辑**:
- 统一管理三种工单类型
- 从维保计划生成或手动创建
- 状态流转：未进行 → 待确认 → 执行中 → 已完成/已退回

---

### 2.4 periodic_inspection（定期巡检单表）

**表名**: `periodic_inspection`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| inspection_id | String(50) | 是 | - | 工单编号（唯一，前缀XJ） |
| project_id | String(50) | 是 | - | 项目编号（外键） |
| project_name | String(200) | 是 | - | 项目名称 |
| plan_start_date | DateTime | 是 | - | 计划开始日期 |
| plan_end_date | DateTime | 是 | - | 计划结束日期 |
| client_name | String(100) | 否 | - | 客户单位 |
| maintenance_personnel | String(100) | 否 | - | 运维人员 |
| status | String(20) | 是 | 未进行 | 状态 |
| filled_count | Integer | 否 | 0 | 已填写检查项数量 |
| total_count | Integer | 否 | 5 | 检查项总数量 |
| remarks | String(500) | 否 | - | 备注 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_periodic_inspection_id`: inspection_id
- `idx_periodic_project_id`: project_id
- `idx_periodic_project_name`: project_name
- `idx_periodic_client_name`: client_name
- `idx_periodic_status`: status
- `idx_periodic_plan_start_date`: plan_start_date

**业务逻辑**:
- 定期巡检工单
- 编号规则：XJ-项目编号-YYYYMMDD
- 员工填写巡检结果，主管审批

---

### 2.5 temporary_repair（临时维修单表）

**表名**: `temporary_repair`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| repair_id | String(50) | 是 | - | 维修单编号（唯一，前缀WX） |
| project_id | String(50) | 是 | - | 项目编号（外键） |
| project_name | String(200) | 是 | - | 项目名称 |
| plan_start_date | DateTime | 是 | - | 计划开始日期 |
| plan_end_date | DateTime | 是 | - | 计划结束日期 |
| client_name | String(100) | 否 | - | 客户单位 |
| maintenance_personnel | String(100) | 否 | - | 运维人员 |
| status | String(20) | 是 | 未进行 | 状态 |
| remarks | String(500) | 否 | - | 备注 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_temp_repair_id`: repair_id
- `idx_temp_project_id`: project_id
- `idx_temp_project_name`: project_name
- `idx_temp_client_name`: client_name
- `idx_temp_status`: status
- `idx_temp_plan_start_date`: plan_start_date

**业务逻辑**:
- 临时维修工单
- 编号规则：WX-项目编号-YYYYMMDD
- 处理突发设备故障

---

### 2.6 spot_work（零星用工单表）

**表名**: `spot_work`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| work_id | String(50) | 是 | - | 用工单编号（唯一，前缀YG） |
| project_id | String(50) | 是 | - | 项目编号（外键） |
| project_name | String(200) | 是 | - | 项目名称 |
| plan_start_date | DateTime | 是 | - | 计划开始日期 |
| plan_end_date | DateTime | 是 | - | 计划结束日期 |
| client_name | String(100) | 否 | - | 客户单位 |
| maintenance_personnel | String(100) | 否 | - | 运维人员 |
| status | String(20) | 是 | 未进行 | 状态 |
| remarks | String(500) | 否 | - | 备注 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_spot_work_id`: work_id
- `idx_spot_project_id`: project_id
- `idx_spot_project_name`: project_name
- `idx_spot_client_name`: client_name
- `idx_spot_status`: status
- `idx_spot_plan_start_date`: plan_start_date

**业务逻辑**:
- 零星用工工单
- 编号规则：YG-项目编号-YYYYMMDD
- 需要班组签字、工人身份证拍照（正反面）

---

## 三、巡检事项配置表

### 3.1 inspection_item（巡检事项表）

**表名**: `inspection_item`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | Integer | 是 | 自增 | 主键ID |
| item_code | String(50) | 是 | - | 事项编码（唯一） |
| item_name | String(200) | 是 | - | 事项名称 |
| item_type | String(50) | 是 | - | 事项类型 |
| level | Integer | 否 | 1 | 层级: 1-项目类型, 2-系统类型, 3-检查项 |
| parent_id | Integer | 否 | - | 父节点ID（自关联） |
| check_content | Text | 否 | - | 检查内容 |
| check_standard | Text | 否 | - | 检查标准 |
| sort_order | Integer | 否 | 0 | 排序 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**业务逻辑**:
- 树形结构配置巡检项目
- 由部门经理维护
- 用于工单填写时的检查项选择
- 三级结构：项目类型 → 系统类型 → 检查项

---

## 四、备品备件管理表

### 4.1 spare_parts_stock（备品备件库存表）

**表名**: `spare_parts_stock`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| product_name | String(200) | 是 | - | 产品名称 |
| brand | String(100) | 否 | - | 品牌 |
| model | String(100) | 否 | - | 产品型号 |
| unit | String(20) | 是 | 件 | 单位 |
| quantity | Integer | 是 | 0 | 库存数量 |
| status | String(20) | 是 | 在库 | 状态：在库/已使用/缺货 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_product_name_brand_model`: product_name, brand, model
- `idx_spare_parts_status`: status

**状态流转**:
- 入库后状态为"在库"
- 被领用后状态变为"已使用"
- 库存为0时状态为"缺货"

---

### 4.2 spare_parts_usage（备品备件领用表）

**表名**: `spare_parts_usage`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| product_name | String(200) | 是 | - | 产品名称 |
| brand | String(100) | 否 | - | 品牌 |
| model | String(100) | 否 | - | 产品型号 |
| quantity | Integer | 是 | - | 领用数量 |
| user_name | String(100) | 是 | - | 领用人员 |
| issue_time | DateTime | 是 | - | 领用时间 |
| unit | String(20) | 是 | 件 | 单位 |
| project_id | String(50) | 否 | - | 项目编号 |
| project_name | String(200) | 否 | - | 项目名称 |
| stock_id | BigInteger | 否 | - | 库存记录ID |
| status | String(20) | 是 | 已使用 | 状态：已使用 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_usage_product_name`: product_name
- `idx_usage_user_name`: user_name
- `idx_usage_project_name`: project_name
- `idx_usage_issue_time`: issue_time
- `idx_usage_status`: status

**业务逻辑**:
- 记录备品备件领用情况
- 关联项目和库存记录
- 领用后扣减库存数量

---

### 4.3 spare_parts_inbound（备品备件入库记录表）

**表名**: `spare_parts_inbound`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| inbound_no | String(50) | 是 | - | 入库单号（唯一） |
| product_name | String(200) | 是 | - | 产品名称 |
| brand | String(100) | 否 | - | 品牌 |
| model | String(100) | 否 | - | 产品型号 |
| quantity | Integer | 是 | - | 入库数量 |
| supplier | String(200) | 否 | - | 供应商 |
| unit | String(20) | 是 | 件 | 单位 |
| user_name | String(100) | 是 | - | 入库人 |
| remarks | String(500) | 否 | - | 备注 |
| created_at | DateTime | 是 | now() | 入库时间 |

**索引**:
- `idx_inbound_no`: inbound_no
- `idx_product_name`: product_name
- `idx_user_name`: user_name
- `idx_created_at`: created_at

**业务逻辑**:
- 记录备品备件入库
- 入库后增加库存数量

---

## 五、维修工具管理表

### 5.1 repair_tools_stock（维修工具库存表）

**表名**: `repair_tools_stock`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| tool_id | String(50) | 否 | - | 工具编号 |
| tool_name | String(200) | 是 | - | 工具名称 |
| category | String(50) | 否 | - | 工具分类 |
| specification | String(200) | 否 | - | 规格型号 |
| unit | String(20) | 是 | 个 | 单位 |
| stock | Integer | 是 | 0 | 库存数量 |
| min_stock | Integer | 否 | 5 | 最低库存预警 |
| location | String(100) | 否 | - | 存放位置 |
| status | String(20) | 是 | 已归还 | 状态：已归还/已领用/已损坏 |
| remark | Text | 否 | - | 备注 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_repair_tool_name`: tool_name
- `idx_repair_tool_category`: category
- `idx_repair_tool_status`: status

**状态流转**:
- 入库后状态为"已归还"
- 领用后状态变为"已领用"
- 归还时损坏状态为"已损坏"

---

### 5.2 repair_tools_issue（维修工具领用表）

**表名**: `repair_tools_issue`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| tool_id | String(50) | 否 | - | 工具编号 |
| tool_name | String(200) | 是 | - | 工具名称 |
| specification | String(200) | 否 | - | 规格型号 |
| quantity | Integer | 是 | - | 领用数量 |
| return_quantity | Integer | 否 | 0 | 归还数量 |
| user_id | BigInteger | 否 | - | 领用人ID |
| user_name | String(100) | 是 | - | 领用人姓名 |
| issue_time | DateTime | 是 | - | 领用时间 |
| return_time | DateTime | 否 | - | 归还时间 |
| project_id | String(50) | 否 | - | 项目编号 |
| project_name | String(200) | 否 | - | 项目名称 |
| status | String(20) | 否 | 已领用 | 状态：已领用/已归还/已损坏 |
| remark | Text | 否 | - | 备注 |
| stock_id | BigInteger | 否 | - | 库存记录ID |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_repair_issue_tool_name`: tool_name
- `idx_repair_issue_user_name`: user_name
- `idx_repair_issue_status`: status
- `idx_repair_issue_issue_time`: issue_time

**业务逻辑**:
- 记录工具领用和归还
- 关联项目和库存记录
- 支持部分归还

---

## 六、基础信息管理表

### 6.1 personnel（人员信息表）

**表名**: `personnel`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| name | String(50) | 是 | - | 姓名 |
| gender | String(10) | 是 | - | 性别 |
| phone | String(20) | 否 | - | 联系电话 |
| department | String(100) | 否 | - | 所属部门 |
| role | String(20) | 是 | 员工 | 角色 |
| address | String(200) | 否 | - | 地址 |
| remarks | String(500) | 否 | - | 备注 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_name`: name
- `idx_department`: department
- `idx_role`: role

**角色说明**:
- 管理员：系统管理、权限配置
- 部门经理：维保计划制定、工单审批、巡检事项维护
- 员工：工单执行、填写提交

---

### 6.2 customer（客户表）

**表名**: `customer`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | Integer | 是 | 自增 | 主键ID |
| name | String(100) | 是 | - | 客户单位 |
| address | String(200) | 否 | - | 客户地址 |
| contact_person | String(50) | 是 | - | 客户联系人 |
| phone | String(20) | 是 | - | 客户联系方式 |
| contact_position | String(50) | 否 | - | 客户联系人职位 |
| remarks | Text | 否 | - | 备注 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**业务逻辑**:
- 管理客户信息
- 可关联到项目信息

---

### 6.3 dictionary（字典表）

**表名**: `dictionary`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| dict_type | String(50) | 是 | - | 字典类型 |
| dict_key | String(50) | 是 | - | 字典键 |
| dict_value | String(200) | 是 | - | 字典值 |
| dict_label | String(200) | 是 | - | 字典标签 |
| sort_order | Integer | 否 | 0 | 排序 |
| is_active | Boolean | 否 | true | 是否启用 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_dict_type`: dict_type
- `idx_dict_key`: dict_key
- `idx_dict_type_key`: dict_type, dict_key

**业务逻辑**:
- 系统配置项管理
- 如：工单类型、状态、维保频率等

---

### 6.4 user_dashboard_config（用户仪表板配置表）

**表名**: `user_dashboard_config`

| 字段名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| id | BigInteger | 是 | 自增 | 主键ID |
| user_id | String(100) | 是 | - | 用户ID |
| dashboard_type | String(50) | 是 | - | 仪表板类型 |
| config | JSON | 是 | - | 配置数据 |
| created_at | DateTime | 是 | now() | 创建时间 |
| updated_at | DateTime | 是 | now() | 更新时间 |

**索引**:
- `idx_user_dashboard`: user_id, dashboard_type

**业务逻辑**:
- 保存用户个性化配置
- 如：列显示、排序等

---

## 七、表间关系图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              project_info (核心)                             │
│                                  项目信息表                                   │
└─────────────────────────────────────────────────────────────────────────────┘
         │              │              │              │              │
         │ FK           │ FK           │ FK           │ FK           │ FK
         ▼              ▼              ▼              ▼              ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│maintenance_  │ │work_plan     │ │periodic_     │ │temporary_    │ │spot_work     │
│plan          │ │工作计划表     │ │inspection    │ │repair        │ │零星用工单表   │
│维保计划表     │ │              │ │定期巡检单表   │ │临时维修单表   │ │              │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
                        │
                        │ 生成
                        ▼
              ┌──────────────────┐
              │ inspection_item  │
              │ 巡检事项表(树形)  │
              └──────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            备品备件管理模块                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  spare_parts_inbound    ──入库──▶  spare_parts_stock                        │
│  (入库记录表)                         (库存表)                               │
│                                          │                                   │
│                                          │ 领用                              │
│                                          ▼                                   │
│                                    spare_parts_usage                         │
│                                    (领用表)                                  │
│                                          │                                   │
│                                          │ FK (project_id)                   │
│                                          ▼                                   │
│                                    project_info                              │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            维修工具管理模块                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  repair_tools_stock  ◀──归还──  repair_tools_issue                          │
│  (工具库存表)         ──领用──▶  (工具领用表)                                 │
│                               │                                              │
│                               │ FK (project_id)                              │
│                               ▼                                              │
│                          project_info                                        │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              基础信息管理                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  personnel (人员表)  ──关联──▶  project_info.project_manager                │
│  customer (客户表)   ──关联──▶  project_info.client_name                    │
│  dictionary (字典表) ──配置──▶  系统各类枚举值                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 八、核心业务流程

### 8.1 工单流转状态

```
未进行 → 待下发(5天内) → 待确认 → 执行中 → 待审批 → 已完成
                                    ↑         │
                                    │         │ 退回
                                    └─────────┘
```

### 8.2 状态说明

| 状态 | 说明 |
|------|------|
| 未进行 | 工单已创建，等待下发 |
| 待下发 | 距离计划开始日期5天内，显示下发按钮 |
| 待确认 | 已下发给员工，等待员工确认 |
| 执行中 | 员工已确认，开始执行工单 |
| 待审批 | 员工已提交，等待主管审批 |
| 已完成 | 主管审批通过，流程结束 |
| 已退回 | 主管审批不通过，退回给员工修改 |

### 8.3 工单编号规则

| 工单类型 | 前缀 | 格式 | 示例 |
|----------|------|------|------|
| 定期巡检单 | XJ | XJ-项目编号-YYYYMMDD | XJ-TQ2023423-20251123 |
| 临时维修单 | WX | WX-项目编号-YYYYMMDD | WX-TQ2023423-20251123 |
| 零星用工单 | YG | YG-项目编号-YYYYMMDD | YG-TQ2023423-20251123 |

---

## 九、数据一致性规则

1. **核心原则**: 所有数据以 `project_info` 表数据为准
2. **外键约束**: 所有关联 `project_id` 的表使用级联删除
3. **软删除**: 所有的删除操作均为非物理删除
4. **数据同步**: 当 `project_info` 表数据变更时，相关联表的数据应同步更新

---

## 十、索引策略

### 10.1 主键索引
- 所有表使用自增主键 `id`

### 10.2 唯一索引
- `project_info.project_id`: 项目编号唯一
- `maintenance_plan.plan_id`: 计划编号唯一
- `work_plan.plan_id`: 工单编号唯一
- `periodic_inspection.inspection_id`: 巡检单编号唯一
- `temporary_repair.repair_id`: 维修单编号唯一
- `spot_work.work_id`: 用工单编号唯一
- `inspection_item.item_code`: 事项编码唯一
- `spare_parts_inbound.inbound_no`: 入库单号唯一

### 10.3 外键索引
- 所有 `project_id` 字段建立索引
- 所有 `status` 字段建立索引
- 所有日期字段建立索引

---

## 十一、数据表清单汇总

| 序号 | 表名 | 中文名称 | 模块 |
|------|------|----------|------|
| 1 | project_info | 项目信息表 | 核心业务 |
| 2 | maintenance_plan | 维保计划表 | 核心业务 |
| 3 | work_plan | 工作计划表 | 核心业务 |
| 4 | periodic_inspection | 定期巡检单表 | 核心业务 |
| 5 | temporary_repair | 临时维修单表 | 核心业务 |
| 6 | spot_work | 零星用工单表 | 核心业务 |
| 7 | inspection_item | 巡检事项表 | 配置管理 |
| 8 | spare_parts_stock | 备品备件库存表 | 物资管理 |
| 9 | spare_parts_usage | 备品备件领用表 | 物资管理 |
| 10 | spare_parts_inbound | 备品备件入库记录表 | 物资管理 |
| 11 | repair_tools_stock | 维修工具库存表 | 物资管理 |
| 12 | repair_tools_issue | 维修工具领用表 | 物资管理 |
| 13 | personnel | 人员信息表 | 基础信息 |
| 14 | customer | 客户表 | 基础信息 |
| 15 | dictionary | 字典表 | 基础信息 |
| 16 | user_dashboard_config | 用户仪表板配置表 | 系统配置 |

---

*文档生成时间: 2025-02-17*
