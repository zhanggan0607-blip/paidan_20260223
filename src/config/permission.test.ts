/**
 * PC端权限配置测试
 * 测试权限判断、菜单权限映射
 */
import { describe, it, expect } from 'vitest'
import {
  hasPermission,
  canShowMenu,
  RoleCode,
  isAdminRole,
  isManagerRole,
  canDeleteWorkOrder,
} from './permission'

describe('PC端权限配置', () => {
  describe('角色判断函数', () => {
    it('isAdminRole（ADMIN_ROLES包含管理员、部门经理、主管）', () => {
      expect(isAdminRole('管理员')).toBe(true)
      expect(isAdminRole('部门经理')).toBe(true)
      expect(isAdminRole('主管')).toBe(true)
      expect(isAdminRole('运维人员')).toBe(false)
      expect(isAdminRole('材料员')).toBe(false)
    })

    it('isManagerRole', () => {
      expect(isManagerRole('管理员')).toBe(true)
      expect(isManagerRole('部门经理')).toBe(true)
      expect(isManagerRole('运维人员')).toBe(false)
      expect(isManagerRole('材料员')).toBe(false)
    })

    it('canDeleteWorkOrder', () => {
      expect(canDeleteWorkOrder('管理员')).toBe(true)
      expect(canDeleteWorkOrder('部门经理')).toBe(true)
      expect(canDeleteWorkOrder('运维人员')).toBe(false)
    })
  })

  describe('hasPermission', () => {
    it('管理员应有所有权限', () => {
      expect(hasPermission('管理员', 'view_statistics')).toBe(true)
      expect(hasPermission('管理员', 'view_project_management')).toBe(true)
      expect(hasPermission('管理员', 'view_personnel')).toBe(true)
      expect(hasPermission('管理员', 'view_work_order')).toBe(true)
    })

    it('运维人员不应有项目管理和人员管理权限', () => {
      expect(hasPermission('运维人员', 'view_project_management')).toBe(false)
      expect(hasPermission('运维人员', 'view_personnel')).toBe(false)
    })

    it('运维人员有统计查看权限（STATISTICS_VIEW_ROLES包含运维人员）', () => {
      expect(hasPermission('运维人员', 'view_statistics')).toBe(true)
    })

    it('运维人员应能查看工单', () => {
      expect(hasPermission('运维人员', 'view_work_order')).toBe(true)
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
      expect(hasPermission('材料员', 'view_spare_parts_stock')).toBe(true)
    })

    it('材料员不能查看工单', () => {
      expect(hasPermission('材料员', 'view_work_order')).toBe(false)
    })

    it('只有管理员能删除人员', () => {
      expect(hasPermission('管理员', 'delete_personnel')).toBe(true)
      expect(hasPermission('部门经理', 'delete_personnel')).toBe(false)
    })

    it('只有管理员能修改角色', () => {
      expect(hasPermission('管理员', 'edit_personnel_role')).toBe(true)
      expect(hasPermission('部门经理', 'edit_personnel_role')).toBe(false)
    })
  })

  describe('canShowMenu', () => {
    it('管理员应能看到所有菜单', () => {
      expect(canShowMenu('statistics', '管理员')).toBe(true)
      expect(canShowMenu('project-info', '管理员')).toBe(true)
      expect(canShowMenu('personnel', '管理员')).toBe(true)
      expect(canShowMenu('work-plan', '管理员')).toBe(true)
    })

    it('运维人员不应看到项目管理和人员管理菜单', () => {
      expect(canShowMenu('project-info', '运维人员')).toBe(false)
      expect(canShowMenu('personnel', '运维人员')).toBe(false)
    })

    it('运维人员能看到统计菜单（STATISTICS_VIEW_ROLES包含运维人员）', () => {
      expect(canShowMenu('statistics', '运维人员')).toBe(true)
    })

    it('运维人员应能看到工单菜单', () => {
      expect(canShowMenu('work-plan', '运维人员')).toBe(true)
      expect(canShowMenu('temporary-repair', '运维人员')).toBe(true)
    })

    it('材料员应能看到备件菜单', () => {
      expect(canShowMenu('spare-parts-stock', '材料员')).toBe(true)
      expect(canShowMenu('spare-parts-issue', '材料员')).toBe(true)
    })

    it('材料员不应看到工单菜单', () => {
      expect(canShowMenu('work-plan', '材料员')).toBe(false)
    })

    it('空角色应返回false', () => {
      expect(canShowMenu('statistics', null)).toBe(false)
      expect(canShowMenu('statistics', undefined)).toBe(false)
    })

    it('未映射的菜单应返回false', () => {
      expect(canShowMenu('unknown-menu', '管理员')).toBe(false)
    })
  })
})
