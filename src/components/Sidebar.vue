<script setup lang="ts">
import type { MenuItem } from '@/types'
import { ref, onMounted } from 'vue'
import { version as appVersion } from '../../package.json'

defineProps<{
  filteredMenuItems: MenuItem[]
  expandedMenus: string[]
  activeMenu: string
}>()

const emit = defineEmits<{
  toggleMenu: [menuId: string]
  handleMenuClick: [item: MenuItem]
}>()

const serverVersion = ref(appVersion)

onMounted(async () => {
  try {
    const res = await fetch('/api/v1/health')
    const data = await res.json()
    if (data.version) {
      serverVersion.value = data.version
    }
  } catch {}
})
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar__header">
      <div class="sidebar__logo">
        <svg
          class="sidebar__logo-icon"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <path d="M12 2L2 7l10 5 10-5-10-5z" />
          <path d="M2 17l10 5 10-5" />
          <path d="M2 12l10 5 10-5" />
        </svg>
      </div>
      <h1 class="sidebar__title">
        SSTCP
      </h1>
      <span class="sidebar__subtitle">维保管理</span>
    </div>
    <nav class="sidebar__nav">
      <div
        v-for="menu in filteredMenuItems"
        :key="menu.id"
        class="nav-group"
      >
        <div
          class="nav-group__title"
          :class="{ 'nav-group__title--expandable': menu.children }"
          @click="emit('toggleMenu', menu.id)"
        >
          <span class="nav-group__label">{{ menu.label }}</span>
          <span
            v-if="menu.children"
            class="nav-group__arrow"
            :class="{ 'nav-group__arrow--open': expandedMenus.includes(menu.id) }"
          >
            <svg
              width="12"
              height="12"
              viewBox="0 0 12 12"
            >
              <path
                d="M4.5 2.5L8 6L4.5 9.5"
                stroke="currentColor"
                stroke-width="1.5"
                fill="none"
              />
            </svg>
          </span>
        </div>
        <Transition name="submenu">
          <div
            v-if="menu.children && expandedMenus.includes(menu.id)"
            class="nav-group__submenu"
          >
            <div
              v-for="submenu in menu.children"
              :key="submenu.id"
              class="nav-item"
              :class="{ 'nav-item--active': activeMenu === submenu.id }"
              @click="emit('handleMenuClick', submenu)"
            >
              <span class="nav-item__dot" />
              <span class="nav-item__text">{{ submenu.label }}</span>
            </div>
          </div>
        </Transition>
        <div
          v-if="!menu.children"
          class="nav-item"
          :class="{ 'nav-item--active': activeMenu === menu.id }"
          @click="emit('handleMenuClick', menu)"
        >
          <span class="nav-item__dot" />
          <span class="nav-item__text">{{ menu.label }}</span>
        </div>
      </div>
    </nav>
    <div class="sidebar__footer">
      <div class="sidebar__version">
        V{{ serverVersion }}
      </div>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  background: var(--color-sidebar-bg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.sidebar::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  bottom: 0;
  width: 1px;
  background: var(--color-sidebar-border);
}

.sidebar__header {
  padding: var(--space-5) var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-2);
  border-bottom: 1px solid var(--color-sidebar-border);
}

.sidebar__logo {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary-light);
  flex-shrink: 0;
}

.sidebar__logo-icon {
  width: 24px;
  height: 24px;
}

.sidebar__title {
  font-family: var(--font-mono);
  font-size: var(--text-lg);
  font-weight: var(--weight-bold);
  color: var(--color-sidebar-text-active);
  letter-spacing: 0.08em;
  line-height: 1;
}

.sidebar__subtitle {
  font-size: var(--text-xs);
  color: var(--color-sidebar-text);
  opacity: 0.6;
  margin-left: auto;
  letter-spacing: 0.04em;
}

.sidebar__nav {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-2) 0;
}

.nav-group {
  margin-bottom: 1px;
}

.nav-group__title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-2) var(--space-4);
  cursor: pointer;
  transition: background var(--transition-fast);
  font-size: var(--text-sm);
  font-weight: var(--weight-semibold);
  color: var(--color-sidebar-text);
  letter-spacing: 0.02em;
  user-select: none;
}

.nav-group__title:hover {
  background: var(--color-sidebar-hover);
}

.nav-group__title--expandable {
  cursor: pointer;
}

.nav-group__arrow {
  display: flex;
  align-items: center;
  color: var(--color-sidebar-text);
  opacity: 0.4;
  transition: transform var(--transition-normal), opacity var(--transition-fast);
}

.nav-group__arrow--open {
  transform: rotate(90deg);
  opacity: 0.7;
}

.nav-group__submenu {
  overflow: hidden;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-1) var(--space-4) var(--space-1) var(--space-6);
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast);
  font-size: var(--text-sm);
  color: var(--color-sidebar-text);
  opacity: 0.75;
  user-select: none;
}

.nav-item:hover {
  background: var(--color-sidebar-hover);
  opacity: 1;
}

.nav-item--active {
  background: var(--color-sidebar-active);
  color: var(--color-sidebar-text-active);
  opacity: 1;
}

.nav-item__dot {
  width: 4px;
  height: 4px;
  border-radius: var(--radius-full);
  background: currentColor;
  opacity: 0.4;
  flex-shrink: 0;
}

.nav-item--active .nav-item__dot {
  opacity: 1;
  background: var(--color-primary-light);
}

.nav-item__text {
  line-height: var(--leading-tight);
}

.sidebar__footer {
  padding: var(--space-3) var(--space-4);
}

.sidebar__version {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--color-sidebar-text);
  opacity: 0.35;
  letter-spacing: 0.06em;
}

.submenu-enter-active,
.submenu-leave-active {
  transition: all var(--transition-normal);
  overflow: hidden;
}

.submenu-enter-from,
.submenu-leave-to {
  opacity: 0;
  max-height: 0;
}

.submenu-enter-to,
.submenu-leave-from {
  opacity: 1;
  max-height: 500px;
}
</style>
