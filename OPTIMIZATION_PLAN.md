# SSTCP 维保管理系统 - 项目优化执行计划

> 基于代码评估报告整理的可执行建议
> 创建日期：2026-03-05
> 预计总工期：4-6 周

---

## 📋 执行计划概览

| 阶段               | 任务数量 | 预计工期 | 风险等级 |
| ------------------ | -------- | -------- | -------- |
| 第一阶段：立即执行 | 3 项     | 1-2 天   | 低       |
| 第二阶段：短期执行 | 4 项     | 1 周     | 低-中    |
| 第三阶段：中期执行 | 3 项     | 2 周     | 中       |
| 第四阶段：长期执行 | 2 项     | 2-3 周   | 低       |

---

## 🚀 第一阶段：立即执行（优先级：高）

### 任务 1.1：移除 CI 中 lint 的 continue-on-error

**问题描述**：
CI 配置中前端 lint 步骤使用 `continue-on-error: true`，导致 lint 失败不会阻断后续流程，可能掩盖代码质量问题。

**影响范围**：

- `.github/workflows/deploy.yml` 第 31、43、107 行

**执行步骤**：

```yaml
# 修改前
- name: Lint PC frontend
  run: npm run lint
  continue-on-error: true # 删除此行

# 修改后
- name: Lint PC frontend
  run: npm run lint
```

**验证方法**：

1. 提交修改后触发 CI
2. 确认 lint 失败时 CI 会正确中断

**回滚方案**：
如需临时跳过 lint，可在特定 commit message 中使用 `[skip ci]`

---

### 任务 1.2：修复现有 lint 错误

**问题描述**：
移除 continue-on-error 后，需要确保现有代码通过 lint 检查。

**执行步骤**：

```bash
# 在项目根目录执行
npm run lint

# 在 H5 目录执行
cd H5 && npm run lint
```

**预期产出**：

- 修复所有 lint 报错
- 更新 eslint.config.js 如有需要

---

### 任务 1.3：确保 typecheck 通过

**执行步骤**：

```bash
# PC 端
npm run typecheck

# H5 端
cd H5 && npm run typecheck
```

---

## 📅 第二阶段：短期执行（优先级：中高）

### 任务 2.1：启用 TypeScript 未使用变量检查

**问题描述**：
`noUnusedLocals` 和 `noUnusedParameters` 设为 false，可能掩盖未使用代码。

**影响范围**：

- `tsconfig.json`
- `H5/tsconfig.json`

**执行步骤**：

**Step 1：渐进式启用（先警告）**

```json
// tsconfig.json
{
  "compilerOptions": {
    "noUnusedLocals": false, // 暂时保持
    "noUnusedParameters": false
    // 新增：仅报告但不阻止编译
  }
}
```

**Step 2：修复警告后正式启用**

```json
{
  "compilerOptions": {
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

**修复策略**：

1. 运行 `npm run typecheck` 收集所有警告
2. 逐个文件修复（从 src/ 开始，再到 H5/src/）
3. 对于暂时保留的变量，使用 `_` 前缀标记

**示例**：

```typescript
// 修复前
function handleClick(event: MouseEvent, index: number) {
  console.log(index) // event 未使用
}

// 修复后
function handleClick(_event: MouseEvent, index: number) {
  console.log(index)
}
```

---

### 任务 2.2：优化 build:all 脚本

**问题描述**：
PC 和 H5 都依赖 `packages/shared`，但共享库未预先编译，可能导致类型不一致。

**当前配置**：

```json
// package.json
"build:all": "npm run build && cd H5 && npm run build"
```

**优化方案**：

```json
{
  "scripts": {
    "build:shared": "cd packages/shared && npm run build",
    "build:pc": "npm run build",
    "build:h5": "cd H5 && npm run build",
    "build:all": "npm run build:shared && npm run build:pc && npm run build:h5",
    "build:all:parallel": "npm run build:shared && npm run build:pc & npm run build:h5 & wait"
  }
}
```

**验证方法**：

```bash
npm run build:all
# 检查 dist/ 和 H5/dist/ 是否正确生成
```

---

### 任务 2.3：添加依赖安全审计

**执行步骤**：

```bash
# 运行安全审计
npm audit

# 自动修复可修复的漏洞
npm audit fix

# 检查 H5 端
cd H5 && npm audit
```

**预期产出**：

- 修复所有高危漏洞
- 记录无法自动修复的漏洞及其风险评估

---

### 任务 2.4：统一锁文件管理

**问题描述**：
Monorepo 需要确保跨工作区的依赖版本一致性。

**执行步骤**：

```bash
# 在根目录重新生成锁文件
rm -rf node_modules package-lock.json
npm install

# 验证工作区依赖
npm ls @sstcp/shared
```

---

## 🔧 第三阶段：中期执行（优先级：中）

### 任务 3.1：优化 CI 构建缓存

**当前问题**：
每次 CI 都重新安装依赖，耗时较长。

**优化方案**：

```yaml
# .github/workflows/deploy.yml
- name: Setup Node.js
  uses: actions/setup-node@v4
  with:
    node-version: '20'
    cache: 'npm'
    cache-dependency-path: |
      package-lock.json
      H5/package-lock.json
      packages/shared/package.json
```

---

### 任务 3.2：分离 CI 任务为独立 Job

**优化目标**：

- PC 前端和 H5 前端可并行构建
- 后端测试独立运行
- 仅在全部通过后才触发部署

**优化方案**：

```yaml
jobs:
  lint:
    # ...

  test-pc:
    needs: lint
    # ...

  test-h5:
    needs: lint
    # ...

  test-backend:
    needs: lint
    # ...

  build:
    needs: [test-pc, test-h5, test-backend]
    # ...

  deploy:
    needs: build
    if: github.ref == 'refs/heads/master'
    # ...
```

---

### 任务 3.3：添加构建产物校验

**执行步骤**：
在 CI 构建后添加校验步骤：

```yaml
- name: Verify build output
  run: |
    test -d dist/assets/js || exit 1
    test -d H5/dist/assets || exit 1
    test -f dist/index.html || exit 1
    test -f H5/dist/index.html || exit 1
```

---

## 📚 第四阶段：长期执行（优先级：低）

### 任务 4.1：创建 CODEBASE.md 文档

**文档结构**：

```markdown
# SSTCP 维保管理系统 - 代码库指南

## 仓库结构

- `/` - PC 端前端（Vue 3 + Vite + Element Plus）
- `/H5` - 移动端前端（Vue 3 + Vite + Vant）
- `/packages/shared` - 共享代码库（类型、工具、API）
- `/backend-python` - 后端服务（FastAPI + PostgreSQL）

## 快速开始

### 环境要求

- Node.js >= 20.0.0
- Python >= 3.11
- PostgreSQL >= 14

### 本地开发

# PC 端

npm run dev

# H5 端

npm run dev:h5

# 后端

npm run dev:backend

## CI/CD 流程

...

## 常见问题

...
```

---

### 任务 4.2：添加共享库使用示例

**在 packages/shared/README.md 中添加**：

````markdown
# @sstcp/shared 使用指南

## 导入示例

### 类型定义

```typescript
import type { ApiResponse, PaginatedResponse } from '@sstcp/shared/types/api'
import type { WorkOrder, Personnel } from '@sstcp/shared/types/models'
```
````

### 工具函数

```typescript
import { formatDateTime, formatCurrency } from '@sstcp/shared/utils/format'
import { getStatusLabel, getStatusColor } from '@sstcp/shared/utils/status'
```

### API 端点

```typescript
import { API_ENDPOINTS } from '@sstcp/shared/api/endpoints'
```

````

---

## ✅ 验收标准

### 第一阶段验收
- [ ] CI lint 失败时能正确中断流程
- [ ] 现有代码通过 lint 检查
- [ ] 现有代码通过 typecheck 检查

### 第二阶段验收
- [ ] TypeScript 严格检查全部启用
- [ ] build:all 脚本正常工作
- [ ] 无高危安全漏洞
- [ ] 依赖版本一致

### 第三阶段验收
- [ ] CI 构建时间减少 30% 以上
- [ ] PC/H5 可并行构建
- [ ] 构建产物校验通过

### 第四阶段验收
- [ ] CODEBASE.md 文档完整
- [ ] 新开发者可在 30 分钟内完成环境搭建

---

## 📊 风险评估

| 风险项 | 影响程度 | 发生概率 | 缓解措施 |
|--------|----------|----------|----------|
| 启用严格检查后大量报错 | 高 | 中 | 渐进式启用，分模块修复 |
| 构建脚本变更导致部署失败 | 高 | 低 | 在 develop 分支先验证 |
| 依赖升级引入兼容性问题 | 中 | 中 | 使用 lock 文件锁定版本 |

---

## 📝 执行记录模板

```markdown
## 执行日期：YYYY-MM-DD

### 执行内容
- [ ] 任务 X.X：任务名称

### 执行结果
- 成功/失败/部分完成

### 遇到的问题
1. 问题描述
   - 解决方案

### 后续行动
- 待处理事项
````

---

## 🔄 计划更新日志

| 日期       | 版本 | 更新内容 | 更新人 |
| ---------- | ---- | -------- | ------ |
| 2026-03-05 | v1.0 | 初始版本 | -      |

---

_此计划将根据执行进度动态更新_
