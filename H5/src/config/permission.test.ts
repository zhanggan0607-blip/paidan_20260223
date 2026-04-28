/**
 * H5端权限配置测试
 * 测试权限判断、角色配置
 */
import { describe, it, expect } from 'vitest'
import {
  hasPermission,
  RoleCode,
  isAdminRole,
  isManagerRole,
  isMaterialManager,
  PERMISSION_CONFIGS,
} from '../config/permission'

describe('权限配置', () => {
  describe('RoleCode', () => {
    it('应包含四种角色', () => {
      expect(RoleCode.ADMIN).toBe('管理员')
      expect(RoleCode.DEPARTMENT_MANAGER).toBe('部门经理')
      expect(RoleCode.MATERIAL_MANAGER).toBe('材料员')
      expect(RoleCode.EMPLOYEE).toBe('运维人员')
    })
  })

  describe('角色判断函数', () => {
    it('isAdminRole（ADMIN_ROLES包含管理员、部门经理、主管）', () => {
      expect(isAdminRole('管理员')).toBe(true)
      expect(isAdminRole('部门经理')).toBe(true)
      expect(isAdminRole('运维人员')).toBe(false)
    })

    it('isManagerRole', () => {
      expect(isManagerRole('管理员')).toBe(true)
      expect(isManagerRole('部门经理')).toBe(true)
      expect(isManagerRole('运维人员')).toBe(false)
      expect(isManagerRole('材料员')).toBe(false)
    })

    it('isMaterialManager（仅材料员返回true）', () => {
      expect(isMaterialManager('管理员')).toBe(false)
      expect(isMaterialManager('部门经理')).toBe(false)
      expect(isMaterialManager('材料员')).toBe(true)
      expect(isMaterialManager('运维人员')).toBe(false)
    })
  })

  describe('hasPermission', () => {
    it('管理员应有所有权限', () => {
      expect(hasPermission('管理员', 'view_statistics')).toBe(true)
      expect(hasPermission('管理员', 'view_project_management')).toBe(true)
      expect(hasPermission('管理员', 'view_personnel')).toBe(true)
    })

    it('运维人员不应有项目管理和人员管理权限', () => {
      expect(hasPermission('运维人员', 'view_project_management')).toBe(false)
      expect(hasPermission('运维人员', 'view_personnel')).toBe(false)
    })

    it('运维人员有统计查看权限', () => {
      expect(hasPermission('运维人员', 'view_statistics')).toBe(true)
    })

    it('运维人员应能查看项目信息', () => {
      expect(hasPermission('运维人员', 'view_project_info')).toBe(true)
    })

    it('空角色应返回false', () => {
      expect(hasPermission(null, 'view_statistics')).toBe(false)
      expect(hasPermission(undefined, 'view_statistics')).toBe(false)
      expect(hasPermission('', 'view_statistics')).toBe(false)
    })

    it('不存在的权限应返回false', () => {
      expect(hasPermission('管理员', 'nonexistent_permission')).toBe(false)
    })

    it('材料员应能查看备件库存', () => {
      expect(hasPermission('材料员', 'view_spare_parts_inventory')).toBe(true)
      expect(hasPermission('材料员', 'view_spare_parts_stock')).toBe(true)
    })

    it('材料员不能查看工单', () => {
      expect(hasPermission('材料员', 'view_work_list')).toBe(false)
      expect(hasPermission('材料员', 'view_temporary_repair')).toBe(false)
    })
  })

  describe('PERMISSION_CONFIGS', () => {
    it('应包含关键权限配置', () => {
      expect(PERMISSION_CONFIGS.view_statistics).toBeDefined()
      expect(PERMISSION_CONFIGS.view_project_management).toBeDefined()
      expect(PERMISSION_CONFIGS.view_personnel).toBeDefined()
      expect(PERMISSION_CONFIGS.view_all_work_orders).toBeDefined()
    })

    it('每个权限配置应有完整字段', () => {
      for (const [id, config] of Object.entries(PERMISSION_CONFIGS)) {
        expect(config.id).toBe(id)
        expect(config.name).toBeTruthy()
        expect(config.description).toBeTruthy()
        expect(Array.isArray(config.allowedRoles)).toBe(true)
        expect(config.allowedRoles.length).toBeGreaterThan(0)
      }
    })
  })
})
