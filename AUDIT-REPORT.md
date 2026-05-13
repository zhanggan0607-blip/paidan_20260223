# 项目全局审查报告

> 审查依据：《个人开发规范标准》
> 审查日期：2026-05-13
> 审查范围：全项目（后端 Python / PC前端 Vue / H5前端 Vue / 公共包 shared / 部署配置）

---

## 审查概要

| 审查维度 | 严重 | 中等 | 轻微 | 合计 |
|----------|:----:|:----:|:----:|:----:|
| 一、文件行数超限（第三章） | 38 | 41 | 0 | **79** |
| 二、代码清洁（第五章·19类检查项） | 12 | 18 | 10 | **40** |
| 三、架构审查（第六章） | 10 | 7 | 2 | **19** |
| 四、安全审查（第七章） | 8 | 7 | 5 | **20** |
| 五、部署与日志（第九章） | 2 | 9 | 4 | **15** |
| 六、测试规范（第八章） | 4 | 4 | 4 | **12** |
| 七、统一化标准（附录） | 1 | 5 | 5 | **11** |
| 八、环境配置与API匹配 | 5 | 10 | 5 | **20** |
| **合计** | **80** | **101** | **35** | **216** |

---

## 一、文件行数超限审查（第三章 3.2）

> 规范要求：每个文件代码量不得超过200行，超过时必须拆分。

### 1.1 后端 Python 文件（38个超限）

| # | 文件路径 | 行数 | 超出倍数 |
|---|----------|:----:|:---------:|
| 1 | `backend-python/app/api/v1/export_pdf.py` | 1499 | 7.5× |
| 2 | `backend-python/app/services/spot_work.py` | 737 | 3.7× |
| 3 | `backend-python/app/services/maintenance_plan.py` | 620 | 3.1× |
| 4 | `backend-python/app/api/v1/repair_tools.py` | 606 | 3.0× |
| 5 | `backend-python/app/services/project_info.py` | 600 | 3.0× |
| 6 | `backend-python/app/api/v1/statistics.py` | 598 | 3.0× |
| 7 | `backend-python/app/api/v1/spot_work.py` | 588 | 2.9× |
| 8 | `backend-python/app/services/periodic_inspection.py` | 534 | 2.7× |
| 9 | `backend-python/app/api/v1/maintenance_log.py` | 507 | 2.5× |
| 10 | `backend-python/app/api/v1/files.py` | 461 | 2.3× |
| 11 | `backend-python/app/api/v1/upload.py` | 431 | 2.2× |
| 12 | `backend-python/app/api/v1/spare_parts.py` | 429 | 2.1× |
| 13 | `backend-python/app/services/sync_service.py` | 412 | 2.1× |
| 14 | `backend-python/app/repositories/spot_work.py` | 410 | 2.1× |
| 15 | `backend-python/app/services/temporary_repair.py` | 401 | 2.0× |
| 16 | `backend-python/app/services/statistics_service.py` | 388 | 1.9× |
| 17 | `backend-python/app/api/v1/weekly_report.py` | 386 | 1.9× |
| 18 | `backend-python/app/services/work_plan.py` | 327 | 1.6× |
| 19 | `backend-python/app/services/weekly_report.py` | 325 | 1.6× |
| 20 | `backend-python/app/main.py` | 318 | 1.6× |
| 21 | `backend-python/app/api/v1/auth.py` | 310 | 1.6× |
| 22 | `backend-python/app/api/v1/admin_edit.py` | 299 | 1.5× |
| 23 | `backend-python/app/api/v1/temporary_repair.py` | 297 | 1.5× |
| 24 | `backend-python/app/utils/aliyun_ocr.py` | 290 | 1.5× |
| 25 | `backend-python/app/api/v1/logs.py` | 276 | 1.4× |
| 26 | `backend-python/app/services/customer.py` | 273 | 1.4× |
| 27 | `backend-python/app/services/auth.py` | 271 | 1.4× |
| 28 | `backend-python/app/dependencies.py` | 267 | 1.3× |
| 29 | `backend-python/app/services/work_order.py` | 260 | 1.3× |
| 30 | `backend-python/app/utils/logging_config.py` | 259 | 1.3× |
| 31 | `backend-python/app/repositories/maintenance_plan.py` | 250 | 1.3× |
| 32 | `backend-python/app/services/personnel.py` | 242 | 1.2× |
| 33 | `backend-python/app/api/v1/periodic_inspection.py` | 236 | 1.2× |
| 34 | `backend-python/app/repositories/base.py` | 228 | 1.1× |
| 35 | `backend-python/app/auth.py` | 223 | 1.1× |
| 36 | `backend-python/app/api/v1/personnel.py` | 223 | 1.1× |
| 37 | `backend-python/app/services/cache.py` | 213 | 1.1× |
| 38 | `backend-python/app/api/v1/work_plan.py` | 192 | — |

### 1.2 PC 前端文件（38个超限）

| # | 文件路径 | 行数 | 超出倍数 |
|---|----------|:----:|:---------:|
| 1 | `src/views/MaintenancePlanManagement.vue` | 3454 | 17.3× |
| 2 | `src/views/StatisticsPage.vue` | 2143 | 10.7× |
| 3 | `src/views/SpotWorkManagement.vue` | 2088 | 10.4× |
| 4 | `src/views/ProjectInfoManagement.vue` | 2086 | 10.4× |
| 5 | `src/views/WorkPlanManagement.vue` | 2038 | 10.2× |
| 6 | `src/views/PeriodicInspectionQuery.vue` | 1858 | 9.3× |
| 7 | `src/views/TemporaryRepairQuery.vue` | 1664 | 8.3× |
| 8 | `src/views/CustomerManagement.vue` | 1640 | 8.2× |
| 9 | `src/views/PersonnelManagement.vue` | 1478 | 7.4× |
| 10 | `src/views/WeeklyReportList.vue` | 1442 | 7.2× |
| 11 | `src/views/MaintenanceLogList.vue` | 1382 | 6.9× |
| 12 | `src/views/SparePartsIssue.vue` | 1346 | 6.7× |
| 13 | `src/views/SparePartsStock.vue` | 1235 | 6.2× |
| 14 | `src/views/RepairToolsIssue.vue` | 1201 | 6.0× |
| 15 | `src/views/RepairToolsInbound.vue` | 1176 | 5.9× |
| 16 | `src/components/WorkerEntryModal.vue` | 1138 | 5.7× |
| 17 | `src/views/NearExpiryReminders.vue` | 1092 | 5.5× |
| 18 | `src/views/SparePartsReturn.vue` | 997 | 5.0× |
| 19 | `src/components/PdfPreviewModal.vue` | 966 | 4.8× |
| 20 | `src/views/RepairToolsReturn.vue` | 935 | 4.7× |
| 21 | `src/views/OverdueAlert.vue` | 934 | 4.7× |
| 22 | `src/views/InspectionItemPage.vue` | 923 | 4.6× |
| 23 | `src/views/TemporaryRepairDetail.vue` | 862 | 4.3× |
| 24 | `src/views/SpotWorkDetail.vue` | 802 | 4.0× |
| 25 | `src/views/SparePartsManagement.vue` | 526 | 2.6× |
| 26 | `src/views/MaintenanceLogFill.vue` | 516 | 2.6× |
| 27 | `src/views/WeeklyReportFill.vue` | 413 | 2.1× |
| 28 | `src/views/LoginPage.vue` | 407 | 2.0× |
| 29 | `src/components/PhotoUpload.vue` | 299 | 1.5× |
| 30 | `src/views/ChangePasswordPage.vue` | 288 | 1.4× |
| 31 | `src/components/Sidebar.vue` | 284 | 1.4× |
| 32 | `src/components/SignaturePad.vue` | 265 | 1.3× |
| 33 | `src/components/Topbar.vue` | 246 | 1.2× |
| 34 | `src/stores/userStore.test.ts` | 240 | 1.2× |
| 35 | `src/config/permission.ts` | 239 | 1.2× |
| 36 | `src/router/index.ts` | 238 | 1.2× |
| 37 | `src/composables/useApiCache.ts` | 216 | 1.1× |
| 38 | `src/stores/userStore.ts` | 212 | 1.1× |

### 1.3 H5 前端文件（35个超限）

| # | 文件路径 | 行数 | 超出倍数 |
|---|----------|:----:|:---------:|
| 1 | `H5/src/views/PeriodicInspectionDetailPage.vue` | 1827 | 9.1× |
| 2 | `H5/src/views/SpotWorkDetailPage.vue` | 1546 | 7.7× |
| 3 | `H5/src/views/TemporaryRepairDetailPage.vue` | 1426 | 7.1× |
| 4 | `H5/src/views/SpotWorkApplyPage.vue` | 1261 | 6.3× |
| 5 | `H5/src/views/WorkerEntryPage.vue` | 1044 | 5.2× |
| 6 | `H5/src/views/MaintenanceLogFillPage.vue` | 736 | 3.7× |
| 7 | `H5/src/views/ProjectInfoPage.vue` | 704 | 3.5× |
| 8 | `H5/src/views/WorkListPage.vue` | 650 | 3.3× |
| 9 | `H5/src/views/HomePage.vue` | 494 | 2.5× |
| 10 | `H5/src/views/RepairToolsStockPage.vue` | 477 | 2.4× |
| 11 | `H5/src/views/RepairToolsIssuePage.vue` | 460 | 2.3× |
| 12 | `H5/src/views/WeeklyReportDetailPage.vue` | 443 | 2.2× |
| 13 | `H5/src/views/SparePartsStockPage.vue` | 438 | 2.2× |
| 14 | `H5/src/views/SparePartsIssuePage.vue` | 431 | 2.2× |
| 15 | `H5/src/views/TemporaryRepairCreatePage.vue` | 422 | 2.1× |
| 16 | `H5/src/stores/userStore.ts` | 394 | 2.0× |
| 17 | `H5/src/views/SparePartsReturnPage.vue` | 393 | 2.0× |
| 18 | `H5/src/views/MaintenanceLogDetailPage.vue` | 391 | 2.0× |
| 19 | `H5/src/views/TemporaryRepairPage.vue` | 366 | 1.8× |
| 20 | `H5/src/views/RepairToolsReturnPage.vue` | 366 | 1.8× |
| 21 | `H5/src/views/SignaturePage.vue` | 365 | 1.8× |
| 22 | `H5/src/views/PeriodicInspectionPage.vue` | 357 | 1.8× |
| 23 | `H5/src/views/SpotWorkPage.vue` | 349 | 1.7× |
| 24 | `H5/src/config/permission.ts` | 269 | 1.3× |
| 25 | `H5/src/views/SpotWorkQuickFillPage.vue` | 293 | 1.5× |
| 26 | `H5/src/views/LoginPage.vue` | 298 | 1.5× |
| 27 | `H5/src/views/ChangePasswordPage.vue` | 285 | 1.4× |
| 28 | `H5/src/views/WeeklyReportListPage.vue` | 250 | 1.3× |
| 29 | `H5/src/router/index.ts` | 245 | 1.2× |
| 30 | `H5/src/views/MaintenanceLogPage.vue` | 256 | 1.3× |
| 31 | `H5/src/views/WeeklyReportAllPage.vue` | 230 | 1.2× |
| 32 | `H5/src/composables/usePhotoUpload.ts` | 225 | 1.1× |
| 33 | `H5/src/stores/userStore.test.ts` | 224 | 1.1× |
| 34 | `H5/src/views/WeeklyReportFillPage.vue` | 217 | 1.1× |
| 35 | `H5/src/services/spotWork.ts` | 206 | 1.0× |

### 1.4 shared 公共包文件（6个超限）

| # | 文件路径 | 行数 | 超出倍数 |
|---|----------|:----:|:---------:|
| 1 | `packages/shared/src/api/request.ts` | 404 | 2.0× |
| 2 | `packages/shared/src/utils/watermark.ts` | 317 | 1.6× |
| 3 | `packages/shared/src/components/SearchInput.vue` | 280 | 1.4× |
| 4 | `packages/shared/src/types/models/common.ts` | 225 | 1.1× |
| 5 | `packages/shared/src/api/endpoints.ts` | 218 | 1.1× |
| 6 | `packages/shared/src/utils/sortInterceptor.ts` | 210 | 1.1× |

### 1.5 行数审查汇总

| 目录 | 总文件数 | 超200行 | 最大文件 | 最大行数 |
|------|:--------:|:-------:|----------|:--------:|
| `backend-python/app/` | ~100 | 37 | export_pdf.py | 1499 |
| `src/` | ~76 | 38 | MaintenancePlanManagement.vue | 3454 |
| `H5/src/` | ~79 | 35 | PeriodicInspectionDetailPage.vue | 1827 |
| `packages/shared/src/` | ~43 | 6 | request.ts | 404 |
| **合计** | ~298 | **116** | — | — |

---

## 二、代码清洁审查（第五章 5.2 · 19类检查项）

### 2.1 废弃即删

| # | 类型 | 问题描述 | 严重程度 |
|---|------|----------|:--------:|
| C-01 | 废弃文件 | `scripts/comprehensive_test_suite.py`、`scripts/security_deep_test.py`、`scripts/test_paidan_site.py` 等脚本未被 CI/CD 引用，可能为废弃文件 | 中 |
| C-02 | 废弃代码 | 后端 `001_initial_sync.py` Alembic 迁移内容为空（仅 `pass`），无实际建表语句 | 高 |
| C-03 | 未使用依赖 | PC端 `vite-plugin-compression` 在 `vite.config.ts` 中未使用 | 低 |
| C-04 | 未使用import | 部分后端文件使用 `logging.getLogger(__name__)` 而非 `get_logger(__name__)`，日志缺少 request_id 上下文 | 低 |

### 2.2 重复即合并

| # | 类型 | 问题描述 | 涉及文件 | 严重程度 |
|---|------|----------|----------|:--------:|
| C-05 | 重复函数 | `decodeJwtPayload` 在3处定义 | PC userStore / H5 userStore / shared request.ts | 高 |
| C-06 | 重复函数 | `isTokenExpired` 在2处定义 | PC userStore / H5 userStore | 高 |
| C-07 | 重复函数 | `fetchCurrentUser` 在2处定义 | PC userStore / H5 userStore | 高 |
| C-08 | 重复函数 | `hasPermission` 在2处定义 | PC permission.ts / H5 permission.ts | 高 |
| C-09 | 重复函数 | 身份证脱敏 `maskIdCard` 在3处定义 | shared idCardValidator / 后端 spot_work service / 前端视图 | 中 |
| C-10 | 重复类 | API缓存 `ApiCache` 在2处定义 | PC useApiCache / H5 apiCache | 中 |
| C-11 | 重复常量 | `valid_statuses` 在后端5个schema文件中重复定义 | temporary_repair / spot_work / periodic_inspection / maintenance_plan / work_plan | 高 |
| C-12 | 重复类型 | `PaginatedResponse` 在PC端3处重新定义 | shared api.ts / PC maintenancePlan / PC inspectionItem | 中 |
| C-13 | 重复类型 | `MaintenancePlanCreate/Update` 在PC和H5各定义一次 | PC maintenancePlan service / H5 maintenancePlan service | 中 |
| C-14 | 重复类型 | `CustomerCreate/Update` 在PC和H5各定义一次 | PC customer service / H5 customer service | 中 |
| C-15 | 重复类型 | `InspectionItemCreate/Update` 在PC和H5各定义一次 | PC inspectionItem service / H5 inspectionItem service | 中 |
| C-16 | 重复配置 | `PERMISSION_CONFIGS` 在PC和H5各定义一次，大量权限项重叠 | PC permission.ts / H5 permission.ts | 高 |
| C-17 | 重复配置 | CSS变量在PC和H5大量重复（颜色/状态/z-index/间距/字体） | PC variables.css / H5 variables.css | 中 |
| C-18 | 重复资源 | 字体文件（4个woff2）在PC和H5完全重复 | PC public/fonts / H5 public/fonts | 低 |
| C-19 | 重复逻辑 | 前端service层8个CRUD service在PC和H5高度重复 | PC services/ / H5 services/ | 高 |
| C-20 | 重复逻辑 | userStore核心逻辑在PC和H5高度重复 | PC userStore / H5 userStore | 高 |
| C-21 | 重复逻辑 | 后端各Repository的 `find_all` 查询模式高度相似 | 5+ Repository文件 | 中 |
| C-22 | 重复逻辑 | 后端各Service的 `partial_update` 逐字段赋值模式重复 | 3+ Service文件 | 中 |

### 2.3 共用即提级

| # | 类型 | 问题描述 | 严重程度 |
|---|------|----------|:--------:|
| C-23 | 可提级 | `decodeJwtPayload` / `isTokenExpired` / `fetchCurrentUser` 被2+模块引用，应提级到 shared | 高 |
| C-24 | 可提级 | `PERMISSION_CONFIGS` 共有权限配置应提级到 shared | 高 |
| C-25 | 可提级 | `hasPermission` 被2端使用，应提级到 shared | 高 |
| C-26 | 可提级 | H5端 `getBaseURL()` 和硬编码 `timeout: 60000` 应使用 shared 的 `API_CONFIG` | 中 |
| C-27 | 可提级 | PC端 composable `index.ts` 缺少 `useApiCache` 和 `useOnlineStatusWebSocket` 导出 | 低 |
| C-28 | 可提级 | H5端 composable `index.ts` 缺少 `usePhotoUpload` 和 `useHeartbeatControl` 导出 | 低 |
| C-29 | 可提级 | PC端 service 中5个API路径硬编码，未使用 `API_ENDPOINTS` 常量 | 中 |
| C-30 | 可提级 | 后端 `WorkOrderStatus` 枚举应替代5个schema中的 `valid_statuses` 重复定义 | 高 |

### 2.4 前后端重复定义

| # | 类型 | 问题描述 | 严重程度 |
|---|------|----------|:--------:|
| C-31 | 枚举重复 | `WorkOrderStatus` 后端Python Enum vs 前端TS常量，值相同形式不同 | 低 |
| C-32 | 枚举重复 | `UserRole` 后端Python Enum vs 前端TS `RoleCode`，值完全一致 | 低 |
| C-33 | 逻辑重复 | 身份证验证逻辑前后端各一份完整实现 | 低 |

---

## 三、架构审查（第六章）

### 3.1 跨层调用（API层直接操作数据库）

| # | 文件 | 问题描述 | 严重程度 |
|---|------|----------|:--------:|
| A-01 | `api/v1/statistics.py` | 整个文件直接在API层操作数据库，绕过Service/Repository层 | 严重 |
| A-02 | `api/v1/repair_tools.py` | 整个文件直接在API层操作数据库，无对应Service/Repository | 严重 |
| A-03 | `api/v1/spare_parts.py` | 大部分端点直接操作数据库，仅1个端点调用Service | 严重 |
| A-04 | `api/v1/spare_parts_stock.py` | 整个文件直接在API层操作数据库 | 严重 |
| A-05 | `api/v1/online_user.py` | 整个文件直接在API层操作数据库 | 严重 |
| A-06 | `api/v1/auth.py` | `reset_password` 端点直接使用 `db.query()` | 中 |
| A-07 | `api/v1/personnel.py` | `_get_online_status_map` 函数直接操作数据库 | 中 |
| A-08 | `api/v1/spot_work.py` | `check_id_card_exists` 直接实例化Repository，绕过Service | 中 |
| A-09 | `api/v1/spot_work.py` | `get_all_workers` 直接使用 `db.query()` | 中 |
| A-10 | `api/v1/export_pdf.py` | 直接实例化多个Repository，绕过Service层 | 中 |

### 3.2 Schema定义位置不当

| # | 文件 | 问题描述 | 严重程度 |
|---|------|----------|:--------:|
| A-11 | `api/v1/spot_work.py` | API层定义 `WorkerInfo`/`QuickFillRequest` 等Pydantic模型，应放schemas层 | 中 |
| A-12 | `api/v1/spare_parts.py` | API层定义 `SparePartsUsageCreate`/`SparePartsReturn` 等模型 | 中 |
| A-13 | `api/v1/spare_parts_stock.py` | API层定义 `SparePartsInboundCreate`/`SparePartsInboundUpdate` 等模型 | 中 |
| A-14 | `api/v1/online_user.py` | API层定义 `OnlineLoginRequest`/`HeartbeatRequest` 等模型 | 中 |

### 3.3 接口设计一致性

| # | 问题描述 | 严重程度 |
|---|----------|:--------:|
| A-15 | 分页响应格式不统一：部分用 `PaginatedResponse`，部分手动构造 `items`/`content`/`total`/`totalElements`/`totalPages` | 中 |
| A-16 | CRUD模式不统一：部分模块缺少Repository/Service层（repair_tools、spare_parts_stock） | 中 |
| A-17 | API路径风格不统一：`/all/list` vs `/workers/all` vs `/{id}` | 低 |

### 3.4 Model缺少Repository层

| # | Model | 状态 | 严重程度 |
|---|-------|------|:--------:|
| A-18 | `SparePartsStock` | 无对应Repository，数据库操作在API层 | 中 |
| A-19 | `SparePartsInbound` | 无对应Repository | 中 |
| A-20 | `RepairToolsStock` / `RepairToolsIssue` / `RepairToolsInbound` | 无对应Repository | 中 |

---

## 四、安全审查（第七章）

### 4.1 高风险问题

| # | 风险领域 | 问题描述 | 严重程度 |
|---|----------|----------|:--------:|
| S-01 | API安全 | OCR身份证识别接口 `/ocr/idcard` 无认证，任何人可调用，泄露身份证信息 | 🔴高 |
| S-02 | 认证鉴权 | 在线用户接口 `/online/login` `/online/logout` 无认证，可伪造任意用户登录/登出状态 | 🔴高 |
| S-03 | 认证鉴权 | WebSocket `/ws/online-status` 无认证，任何人可连接获取在线用户信息 | 🔴高 |
| S-04 | 认证鉴权 | 默认密码策略极弱（手机号后6位或"123456"），且登录锁定功能被禁用 `LOGIN_LOCKOUT_ENABLED = False` | 🔴高 |
| S-05 | API安全 | 钉钉配置检查接口 `/dingtalk/check-config` 无认证，暴露AppKey/AppSecret配置状态 | 🔴高 |
| S-06 | API安全 | 文件访问接口使用可选认证 `get_current_user_info`，未登录用户可访问文件；缩略图和by-id接口完全无认证 | 🔴高 |
| S-07 | SQL注入 | `WorkOrderService._build_order_subquery` 使用f-string拼接SQL，虽然参数来自硬编码，但模式危险 | 🔴高 |
| S-08 | SQL注入 | `main.py` 中动态列迁移使用 `f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_def}"` | 🔴高 |

### 4.2 中风险问题

| # | 风险领域 | 问题描述 | 严重程度 |
|---|----------|----------|:--------:|
| S-09 | 前端安全 | Nginx CSP使用 `unsafe-inline`/`unsafe-eval`/`frame-ancestors *`，严重削弱XSS防护 | 🟡中 |
| S-10 | API安全 | CORS配置包含 `http://localhost`，生产环境不应保留 | 🟡中 |
| S-11 | 认证鉴权 | 多个业务接口使用可选认证，未登录可查看客户列表/统计数据/导出PDF/工作计划/维保计划 | 🟡中 |
| S-12 | 数据安全 | 身份证号码明文存储，API返回完整身份证号（`/workers/all`） | 🟡中 |
| S-13 | API安全 | 限流白名单排除登录和OCR接口，易被暴力攻击 | 🟡中 |
| S-14 | 前端安全 | CSRF中间件跳过Bearer Token请求，若Token存Cookie仍有CSRF风险 | 🟡中 |
| S-15 | API安全 | 迁移API依赖 `debug` 配置限制访问，生产环境误设 `DEBUG=True` 可执行任意SQL | 🟡中 |

### 4.3 低风险问题

| # | 风险领域 | 问题描述 | 严重程度 |
|---|----------|----------|:--------:|
| S-16 | 配置泄露 | `.env.example` 暴露数据库用户名 `sstcp_user` 和数据库名 `tq` | 🟢低 |
| S-17 | 信息泄露 | 健康检查接口无认证，数据库异常时泄露错误信息 | 🟢低 |
| S-18 | 信息泄露 | Prometheus `/metrics` 端点无认证，泄露应用内部指标 | 🟢低 |
| S-19 | 认证鉴权 | Token黑名单内存降级最大10000条，超出清理一半可能误放行 | 🟢低 |
| S-20 | 前端安全 | ESLint `vue/no-v-html` 设为warn，但实际未发现v-html使用 | 🟢低 |

### 4.4 安全亮点（做得好的方面）

| 安全措施 | 状态 |
|---------|------|
| JWT认证体系（HS256 + bcrypt） | ✅ |
| Token黑名单（Redis + 内存降级） | ✅ |
| 密码哈希（bcrypt，截断72字节） | ✅ |
| SECRET_KEY启动检查 | ✅ |
| CSRF中间件（Origin/Referer校验） | ✅ |
| CSP中间件（nonce机制） | ✅ |
| 限流中间件（Redis + 内存降级） | ✅ |
| API文档生产关闭 | ✅ |
| Nginx安全头（HSTS/X-Frame-Options/X-Content-Type-Options） | ✅ |
| HTTPS强制 | ✅ |
| 文件类型校验（filetype库） | ✅ |
| 文件名清理（防路径遍历） | ✅ |
| OCR日志脱敏 | ✅ |
| PDF身份证脱敏 | ✅ |
| .env不在版本控制 | ✅ |
| 图片URL域名白名单 | ✅ |

---

## 五、部署与日志审查（第九章）

### 5.1 部署规范

| # | 问题描述 | 严重程度 |
|---|----------|:--------:|
| D-01 | `docker-compose-server.yml` 不存在（项目规则提到需检查），生产部署可能缺少专用配置 | 高 |
| D-02 | 项目根目录无 `.env` 文件，docker-compose变量无法解析 | 高 |
| D-03 | PC前端和H5前端Dockerfile缺少健康检查 | 中 |
| D-04 | 生产docker-compose前端容器缺少健康检查和资源限制 | 中 |
| D-05 | CD脚本缺少旧版本容器/镜像/挂载卷的完整清理 | 中 |
| D-06 | CD脚本缺少部署验证步骤（容器健康/接口可达/功能链路/数据持久化） | 中 |
| D-07 | `.env.example` 数据库名为 `tq`，与项目规则中的 `sstcp_test` 不一致 | 中 |
| D-08 | `.env.example` 缺少 `ENVIRONMENT`/`PAGE_SIZE`/`MAX_PAGE_SIZE`/`PORT` 字段 | 中 |

### 5.2 日志规范

| # | 问题描述 | 严重程度 |
|---|----------|:--------:|
| L-01 | 缺少 `trace_id` 传递机制，`trace_id` 始终为 `-`，无法跨服务链路追踪 | 高 |
| L-02 | 缺少业务日志：repair_tools/spare_parts/online_user等模块无操作日志 | 中 |
| L-03 | 缺少性能日志：无慢查询/慢接口阈值告警机制 | 中 |
| L-04 | 缺少第三方调用日志：钉钉API调用无请求参数/响应/耗时/状态日志 | 中 |
| L-05 | 日志格式不统一：部分API文件使用 `logging.getLogger` 而非 `get_logger`，缺少request_id | 低 |
| L-06 | 日志级别不可动态调整，无运行时调整接口 | 低 |
| L-07 | 缺少日志集中收集系统（ELK/Loki），仅写入本地文件 | 中 |
| L-08 | 审计日志无防篡改机制，仅存储在数据库中 | 低 |
| L-09 | 部分Service中 `logger.info` 记录过于详细的调试信息，生产环境可能日志过多 | 低 |

### 5.3 TROUBLESHOOTING.md

| # | 问题描述 | 严重程度 |
|---|----------|:--------:|
| T-01 | 文件体积过大（超过228KB），应考虑按年度/模块拆分或归档旧记录 | 中 |
| T-02 | 部分早期记录格式不符合规范（缺少日期标题头/类型/概要/根因字段） | 低 |
| T-03 | 目录索引可能过期，需人工核对 | 低 |

---

## 六、测试规范审查（第八章）

### 6.1 后端测试

| # | 问题描述 | 严重程度 |
|---|----------|:--------:|
| T-04 | 测试文件极少：仅5个测试文件，覆盖模块非常有限 | 严重 |
| T-05 | API测试覆盖面窄：仅覆盖5个模块基本端点，核心业务模块（spot_work/temporary_repair/repair_tools/spare_parts/statistics/customer）无测试 | 严重 |
| T-06 | Service测试覆盖面窄：仅测试BaseService和PersonnelService | 严重 |
| T-07 | 缺少Repository层测试 | 中 |
| T-08 | 缺少E2E测试（规范要求Playwright端到端测试） | 严重 |
| T-09 | 测试覆盖率极低，预计低于10% | 中 |

### 6.2 前端测试

| # | 问题描述 | 严重程度 |
|---|----------|:--------:|
| T-10 | PC端仅2个测试文件（userStore / permission） | 中 |
| T-11 | H5端仅2个测试文件（apiCache / permission） | 中 |
| T-12 | 前端Service层和Composable层完全没有测试 | 中 |
| T-13 | shared包测试覆盖较好（endpoints/debounce/format/searchHistory/status） | — |

---

## 七、统一化标准审查（附录）

### 7.1 命名规范

| # | 问题描述 | 严重程度 |
|---|----------|:--------:|
| U-01 | 后端所有Service类均未使用 `Impl` 后缀（规范要求），如 `SpotWorkService` 应为 `SpotWorkServiceImpl` | 中 |
| U-02 | H5端 `useHeartbeatControl` 导出对象而非函数，不符合Vue Composable标准写法 | 低 |
| U-03 | PC端composable `index.ts` 缺少 `useApiCache` 和 `useOnlineStatusWebSocket` 导出 | 低 |
| U-04 | H5端composable `index.ts` 缺少 `usePhotoUpload` 和 `useHeartbeatControl` 导出 | 低 |

### 7.2 权限定义一致性

| # | 问题描述 | 严重程度 |
|---|----------|:--------:|
| U-05 | `MANAGER_ROLES` 定义冲突：`dependencies.py` 包含"主管"，`enums.py` 不包含 | 🔴高 |
| U-06 | `PersonnelConfig.VALID_ROLES` 缺少"主管"角色，可能导致创建主管角色人员时被拒绝 | 中 |
| U-07 | 权限检查分散硬编码：`auth.py` 中 `if role not in ['管理员', '部门经理', '主管']` | 中 |
| U-08 | `spare_parts_stock.py` 硬编码 `MATERIAL_MANAGER_ROLE = '材料员'`，未使用统一依赖 | 中 |
| U-09 | PC端和H5端权限定义数量差异大（15 vs 30+），H5端有大量PC端没有的权限 | 中 |
| U-10 | H5端 `view_department_weekly_report` 的 `allowedRoles` 与共享定义不一致 | 中 |

---

## 八、环境配置与API路径匹配

### 8.1 前端定义了但后端没有的API路径

| # | 前端路径 | 严重程度 |
|---|----------|:--------:|
| E-01 | `USER_DASHBOARD_CONFIG.GET` (`/user-dashboard-config`) | 高 |
| E-02 | `USER_DASHBOARD_CONFIG.UPDATE` (`/user-dashboard-config`) | 高 |
| E-03 | `WORK_ORDER.DETAIL` (`/work-order/{id}`) | 高 |
| E-04 | `PERIODIC_INSPECTION.RECORD_DETAIL` (`/periodic-inspection/{id}/records/{recordId}`) | 中 |
| E-05 | `SPOT_WORK.WORKER_DETAIL` (`/spot-work/workers/{id}`) | 中 |
| E-06 | `OPERATION_TYPE.DETAIL` (`/operation-type/{id}`) | 中 |
| E-07 | `OPERATION_TYPE.BY_CODE` (`/operation-type/code/{code}`) | 中 |

### 8.2 后端有但前端未定义的API路径（主要路径）

| # | 后端路由 | 严重程度 |
|---|----------|:--------:|
| E-08 | `GET /export/periodic-inspection/{id}` | 中 |
| E-09 | `GET /export/temporary-repair/{id}` | 中 |
| E-10 | `GET /export/spot-work/{id}` | 中 |
| E-11 | `GET /export/periodic-maintenance/{id}` | 中 |
| E-12 | `POST /auth/change-password` | 中 |
| E-13 | `POST /auth/reset-password` | 中 |
| E-14 | `GET /maintenance-plan/project/{project_id}` | 中 |
| E-15 | `GET /maintenance-plan/upcoming/list` | 中 |
| E-16 | `PATCH /maintenance-plan/{id}/status` | 中 |
| E-17 | `POST /admin-edit/*` (4个端点) | 中 |
| E-18 | `GET /statistics/repair-stats` 等4个统计端点 | 中 |

> 注：后端有约40+个路径前端 `endpoints.ts` 未定义，其中大部分是管理/诊断/迁移类接口（低优先级），上表列出的是业务核心路径。

---

## 九、问题优先级修复建议

### P0 — 必须立即修复

| 编号 | 问题 | 影响 |
|------|------|------|
| S-01 | OCR接口无认证 | 身份证信息泄露、阿里云费用滥用 |
| S-02 | 在线用户接口无认证 | 可伪造任意用户登录/登出 |
| S-03 | WebSocket无认证 | 信息泄露 |
| S-04 | 默认密码极弱+锁定禁用 | 暴力破解风险 |
| S-06 | 文件访问接口认证不严格 | 敏感文件泄露 |
| U-05 | MANAGER_ROLES定义冲突 | 权限判断不一致 |
| E-01~E-03 | 前端API路径后端不存在 | 前端调用404 |

### P1 — 尽快修复

| 编号 | 问题 | 影响 |
|------|------|------|
| A-01~A-05 | 5个API文件完全绕过Service/Repository层 | 架构混乱、难以维护 |
| C-05~C-08 | JWT/权限相关函数3端重复 | 维护成本高、易不同步 |
| C-11 | valid_statuses 5处重复定义 | 枚举值易不同步 |
| C-16 | PERMISSION_CONFIGS两端重复 | 权限配置易不同步 |
| C-19~C-20 | service层/userStore核心逻辑PC/H5重复 | 维护成本高 |
| S-07~S-08 | SQL拼接模式 | 潜在注入风险 |
| S-11 | 业务接口使用可选认证 | 未授权数据访问 |
| S-12 | 身份证号明文存储 | 数据泄露风险 |
| L-01 | 缺少trace_id传递 | 无法链路追踪 |
| D-01 | 生产docker-compose缺失 | 部署风险 |

### P2 — 计划修复

| 编号 | 问题 | 影响 |
|------|------|------|
| C-09~C-10 | 脱敏/缓存函数重复 | 维护成本 |
| C-12~C-15 | 类型定义重复 | 类型不同步 |
| C-17 | CSS变量重复 | 样式不同步 |
| C-21~C-22 | Repository/Service模式重复 | 代码冗余 |
| A-06~A-10 | 部分端点跨层调用 | 架构不统一 |
| A-11~A-14 | Schema定义位置不当 | 代码组织混乱 |
| A-15~A-17 | 接口设计不一致 | 前后端对接困难 |
| S-09~S-15 | 中等安全风险 | 安全隐患 |
| T-04~T-12 | 测试覆盖极低 | 质量保障缺失 |
| D-02~D-08 | 部署配置不完善 | 运维风险 |
| L-02~L-09 | 日志规范不足 | 问题排查困难 |

---

## 十、最终质量评估

| 维度 | 评分 | 说明 |
|------|:----:|------|
| 功能完整性 | ⭐⭐⭐⭐ | 核心业务功能完整，但部分前端定义的API后端未实现 |
| 代码规范 | ⭐⭐ | 116个文件超200行限制；大量重复代码未合并/提级 |
| 架构设计 | ⭐⭐ | 5个API文件完全绕过三层架构；接口设计不统一 |
| 安全性 | ⭐⭐⭐ | 基础安全措施完善（JWT/CSRF/CSP/限流），但6个高风险问题需修复 |
| 可维护性 | ⭐⭐ | 测试覆盖率极低；大量重复代码；日志规范不足 |
| 可复用性 | ⭐⭐ | shared包已建立但两端未充分使用；大量可提级代码 |
| 部署规范 | ⭐⭐⭐ | Docker化部署已实现，但生产配置缺失、部署验证不完整 |
| 兼容性 | ⭐⭐⭐⭐ | PC端和H5端功能覆盖良好，响应式适配到位 |

> **综合评估**：项目功能完整，基础安全措施到位，但在代码规范（行数限制/重复代码）、架构一致性（三层架构遵循）、测试覆盖、日志规范等方面存在较大改进空间。建议按 P0 → P1 → P2 优先级逐步修复。
