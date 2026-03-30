import { test, expect } from '@playwright/test'

test.describe('维保计划管理', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('应该能够成功保存维保计划', async ({ page }) => {
    await page.goto('/maintenance-plan')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('.maintenance-plan-management')).toBeVisible()

    const addButton = page.locator('button:has-text("新增维保计划")')
    await addButton.click()

    await page.waitForSelector('.modal-container', { state: 'visible' })

    const projectSelect = page.locator('.el-select').first()
    await projectSelect.click()

    await page.waitForSelector('.el-select-dropdown', { state: 'visible' })

    const firstOption = page.locator('.el-select-dropdown__item').first()
    if (await firstOption.isVisible()) {
      await firstOption.click()

      await page.waitForTimeout(1000)

      const saveButton = page.locator('button:has-text("保存")')
      await saveButton.click()

      await page.waitForTimeout(2000)

      const toast = page.locator('.toast-message, .el-message')
      const toastText = await toast.textContent().catch(() => null)

      console.log('Toast message:', toastText)

      await expect(page.locator('.modal-container')).not.toBeVisible({ timeout: 10000 })
    } else {
      console.log('No project options available')
    }
  })
})

test.describe('登录功能', () => {
  test('应该能够显示登录页面', async ({ page }) => {
    await page.goto('/')

    await expect(page).toHaveURL(/login|\/$/)

    const loginForm = page.locator('form, .login-form, .login-page')
    await expect(loginForm).toBeVisible()
  })
})

test.describe('统计页面', () => {
  test('应该能够正确显示统计数据', async ({ page }) => {
    await page.goto('/statistics')
    await page.waitForLoadState('networkidle')

    await expect(page.locator('.statistics-page')).toBeVisible()

    const yearSelector = page.locator('.year-select')
    await expect(yearSelector).toBeVisible()

    const miniCards = page.locator('.mini-card')
    await expect(miniCards.first()).toBeVisible()
  })
})
